FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
# Install CPU-only torch to avoid downloading 2GB+ of CUDA libraries
RUN pip install --no-cache-dir --user torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Create a system group and user with a home directory
RUN groupadd -r nexusai && useradd -m -r -g nexusai nexusai

COPY --from=builder /root/.local /home/nexusai/.local
COPY . .
RUN chown -R nexusai:nexusai /app

ENV PATH=/home/nexusai/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER nexusai

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

