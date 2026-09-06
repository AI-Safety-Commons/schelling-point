FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BOARD_HOST=0.0.0.0 BOARD_PORT=3000 BOARD_DB=/data/messages.db
WORKDIR /app
COPY app.py .
RUN mkdir -p /data && chown -R nobody:nogroup /app /data
USER nobody
EXPOSE 3000
HEALTHCHECK --interval=5s --timeout=2s --start-period=2s --retries=10 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=1)"]
CMD ["python", "app.py"]
