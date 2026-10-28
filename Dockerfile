FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY youtube_bot ./youtube_bot

CMD ["python", "-m", "youtube_bot.main"]
