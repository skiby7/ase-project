FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 9190

CMD ["uvicorn", "app:test", "--host", "0.0.0.0", "--port", "9190","--ssl-keyfile=/run/secrets/key","--ssl-certfile=/run/secrets/cert"]