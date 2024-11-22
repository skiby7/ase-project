FROM python:3.12-slim

WORKDIR /app

COPY app.py .
COPY requirements.txt .
COPY distros.txt .
COPY db.py .

RUN pip install -r requirements.txt

EXPOSE 5000

#CMD flask run --host=0.0.0.0 --port=5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]