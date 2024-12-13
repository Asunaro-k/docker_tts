import groq
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from tempfile import NamedTemporaryFile
import ffmpeg
import io

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

# Example usage with Streamlit:
def main():
    st.title("Voice to Text Transcription")
    
    # Record audio using Streamlit widget
    audio_bytes = audio_recorder(pause_threshold=30)
    
    if audio_bytes:
        # Convert audio if necessary (e.g., from wav to mp3)
        audio_bytes = convert_audio_format(audio_bytes, target_format="mp3")
        
        # Convert audio to text using Groq API
        transcript = transcribe_audio_to_text(audio_bytes)
        
        if transcript:
            st.write("Transcribed Text:", transcript)
        else:
            st.write("Transcription failed.")

if __name__ == "__main__":
    main()
