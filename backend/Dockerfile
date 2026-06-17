FROM python:3.12-slim AS builder

WORKDIR /app

# install deps first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

# copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# copy source
COPY . .

# make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
