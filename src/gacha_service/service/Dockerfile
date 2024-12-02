FROM python:3.12-alpine

WORKDIR /app
RUN apk add curl
RUN pip install -r requirements.txt
COPY . .
EXPOSE 9190

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9190","--ssl-keyfile=/run/secrets/key","--ssl-certfile=/run/secrets/cert"]
