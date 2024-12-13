import streamlit as st
import websockets
import asyncio
import groq
import sounddevice as sd
import scipy.io.wavfile as wav
import io
import base64

# Groq APIクライアントの初期化
groq_client = groq.Groq()

# オーディオ録音パラメータ
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5

def record_audio():
    """sounddeviceを使用して音声を録音"""
    st.info("音声録音中...")
    recording = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE), 
        samplerate=SAMPLE_RATE, 
        channels=CHANNELS,
        dtype='int16'
    )
    sd.wait()
    
    # メモリ上のwavファイルとして保存
    wav_buffer = io.BytesIO()
    wav.write(wav_buffer, SAMPLE_RATE, recording)
    wav_buffer.seek(0)
    
    return wav_buffer.getvalue()

async def transcribe_audio(audio_data):
    """Groq APIを使用して音声をテキストに変換"""
    try:
        # Base64エンコードされた音声データ
        base64_audio = base64.b64encode(audio_data).decode('utf-8')
        
        # Groq Whisper APIへのリクエスト
        response = groq_client.audio.transcriptions.create(
            file=base64_audio,
            model="whisper-large-v3-turbo",
            response_format="text"
        )
        
        return response
    except Exception as e:
        st.error(f"文字起こし中にエラーが発生: {e}")
        return ""

def main():
    st.title("Groq Whisper音声文字起こしアプリ")
    
    if st.button("音声録音と文字起こし"):
        # 音声録音
        audio_data = record_audio()
        
        # 文字起こし
        transcription = asyncio.run(transcribe_audio(audio_data))
        
        st.text_area("文字起こし結果:", value=transcription, height=200)

if __name__ == "__main__":
    main()