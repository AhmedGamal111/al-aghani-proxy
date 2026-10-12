FROM python:3.12-slim

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY alagahni.py .

# Standard default port (can be overridden by cloud platform via PORT env var)
ENV PORT=8080
EXPOSE 8080

CMD ["python", "-u", "alagahni.py"]
