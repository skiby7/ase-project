FROM python:3.12-alpine
WORKDIR /code/service
# RUN apt-get update -y && apt-get install -y build-essential
COPY ./requirements.txt /code/requirements.txt
# COPY libs routers config.yml main.py ./
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
EXPOSE 9390
CMD ["python3", "-u", "main.py"]
