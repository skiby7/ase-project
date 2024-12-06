FROM python:3.12-alpine

WORKDIR /app
RUN apk add curl
COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY . .
EXPOSE 9390

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9390","--ssl-keyfile=/run/secrets/auction_key","--ssl-certfile=/run/secrets/auction_cert"]
