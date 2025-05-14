FROM python:3.13-slim

WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# uvをインストール
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係ファイルをコピー
COPY requirements.txt .

# 依存関係をインストール
RUN uv pip install -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# ポートを公開
EXPOSE 8000

# アプリケーションを実行
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 