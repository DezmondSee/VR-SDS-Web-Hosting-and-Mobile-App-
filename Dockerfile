FROM python:3.9-slim

WORKDIR /app

# 1. Install system dependencies for audio and MySQL
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends --fix-missing \
    libsndfile1 \
    ffmpeg \
    default-libmysqlclient-dev \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Upgrade pip and install requirements with a higher timeout
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# 3. Download the NLP Brain for SpaCy
RUN python -m spacy download en_core_web_sm

# 4. Copy all files
COPY . .

# 5. Expose the port for the main portal
EXPOSE 8501

# Default command to run the unified portal
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]