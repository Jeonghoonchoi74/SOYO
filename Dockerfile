FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1 \
PIP_NO_CACHE_DIR=1 \
HF_HOME=/root/.cache/huggingface \
TOKENIZERS_PARALLELISM=false \
PYTHONIOENCODING=UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
git ca-certificates && \
 rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --upgrade pip && \
pip install --index-url https://download.pytorch.org/whl/cpu torch

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY realtime_summarizer.py /app/realtime_summarizer.py
ENV PYTHONWARNINGS="ignore:.*do_sample.*:UserWarning,ignore:.*top_p.*:UserWarning,ignore:.*top_k.*:UserWarning"
CMD ["python", "-m", "realtime_summarizer", "--batch-size", "10", "--write"]
