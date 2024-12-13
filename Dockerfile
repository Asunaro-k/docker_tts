# ベースイメージの設定 (既存のものに追加)
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    python3-pyaudio \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

# 必要なPython依存関係をコピーしてインストール
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY backend/app.py .

# Streamlitのポート
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]