FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080 DB_PATH=/data/harvest.db
RUN mkdir -p /data
EXPOSE 8080
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app
