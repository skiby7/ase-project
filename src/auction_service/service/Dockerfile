FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 9390

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9390","--ssl-keyfile=/run/secrets/auction_key","--ssl-certfile=/run/secrets/auction_cert"]
