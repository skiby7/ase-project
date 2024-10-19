FROM python:3.12-slim
WORKDIR /code/service
RUN apt-get update -y && apt-get install -y build-essential
COPY ./requirements.txt /code/requirements.txt
COPY . .
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
EXPOSE 9093
CMD ["python3", "-u", "main.py"]
