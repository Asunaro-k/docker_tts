import groq
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from tempfile import NamedTemporaryFile
import ffmpeg
import io
import edge_tts
from edge_tts import VoicesManager
import random
import asyncio
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import re

# 音声生成のためのプロンプト
TTS_PROMPT = """
あなたは与えられた文章に対して、以下の判断を行うアシスタントです：
1. この言語が日本語なのか英語なのか

文章: {prompt}

以下の形式で応答してください：
language_jp: [true/false] - 日本語の場合は場合はtrue
"""

def convert_audio_format(audio_bytes, target_format="mp3"):
    import ffmpeg
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()

        with NamedTemporaryFile(delete=True, suffix=f".{target_format}") as converted_file:
            try:
                # overwrite_output() を追加
                ffmpeg.input(temp_file.name).output(converted_file.name).overwrite_output().run()
                # 変換されたファイルの内容を返す
                return converted_file.read()
            except ffmpeg._run.Error as e:
                #print("FFmpeg error:", e.stderr)  # 標準エラー出力を表示
                raise


        
def transcribe_audio_to_text(audio_bytes):
    groq_client = groq.Groq()
    try:
        with NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file.flush()
            with open(temp_file.name, "rb") as audio_file:
                response = groq_client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo", file=audio_file, response_format="text"
                )
                return response
    except groq.BadRequestError as e:
        st.error(f"Error transcribing audio: {e}")
        return None
    

# Text-to-Speech function
async def text_to_speech(text,language="ja"):
    try:
        voices = await VoicesManager.create()  # 非同期関数として呼び出す
        voice = voices.find(Gender="Female", Language=language)
        
        # ユニークな一時ファイルをセッションごとに作成
        if 'tts_audio_path' not in st.session_state:
            temp_file = NamedTemporaryFile(delete=False, suffix=".mp3")
            st.session_state.tts_audio_path = temp_file.name

        # ファイルに音声を保存
        communicate = edge_tts.Communicate(text, random.choice(voice)["Name"])
        await communicate.save(st.session_state.tts_audio_path)  # 非同期で保存

        return st.session_state.tts_audio_path  # ユニークな一時ファイルパスを返す
    except Exception as e:
        st.error(f"Error converting text to speech: {e}")
        return None
    
# Generate text using Groq
def generate_text(prompt):
    groq_client = groq.Groq()
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-70b-versatile"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating text: {e}")
        return None

# Example usage with Streamlit:
def main():
    st.title("Voice to Text Transcription")

    if 'skip_first_attempt' not in st.session_state:
        st.session_state.skip_first_attempt=True


    groq_client = ChatGroq()
    tts_prompt = PromptTemplate(template=TTS_PROMPT, input_variables=["prompt"])
    tts_chain = tts_prompt | groq_client

    
    # Record audio using Streamlit widget
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="3x",
        pause_threshold=5
    )

    if st.session_state.skip_first_attempt:
        if audio_bytes:
            st.warning("Skipping first attempt to allow microphone permissions.")
            st.session_state.skip_first_attempt = False
        return  # 初回は何もしない マイクの許可用
    
    if audio_bytes:
        # Convert audio if necessary (e.g., from wav to mp3)
        audio_bytes = convert_audio_format(audio_bytes, target_format="mp3")
        
        # Convert audio to text using Groq API
        transcript = transcribe_audio_to_text(audio_bytes)
        
        if transcript:
            st.write("Transcribed Text:", transcript)
        else:
            st.write("Transcription failed.")

        prompt = transcript
        if prompt:
            # Generate text
            generated_text = generate_text(prompt)
            
            if generated_text:
                # Display generated text
                st.write("Generated Text:")
                st.write(generated_text)
                language = "ja"
                analysis = asyncio.run(tts_chain.ainvoke(generated_text))
                content = analysis.content if hasattr(analysis, 'content') else str(analysis)
                language_flag = "language_jp: true" in content
                if language_flag:
                    language = "ja"
                else:
                    language = "en"
                # st.markdown(content)
                # st.markdown(language)
                
                # Convert to speech and store in session state
                audio_path = asyncio.run(text_to_speech(generated_text,language))
                
                if audio_path :
                    # Play audio directly from memory
                    st.audio(audio_path, format='audio/mp3')
                    #st.success(f"Audio file saved to temporary location: {st.session_state.tts_audio_path}")
    

if __name__ == "__main__":
    main()
