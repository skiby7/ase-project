FROM python:3.12-slim

WORKDIR /code

RUN apt-get update -y && apt-get install -y build-essential

COPY . .

RUN pip3 install --no-cache-dir --upgrade -r ./requirements.txt

EXPOSE 9090

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "9090"]
