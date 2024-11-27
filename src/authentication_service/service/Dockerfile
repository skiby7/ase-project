FROM python:3.12-slim

WORKDIR /code

RUN apt-get update -y && apt-get install -y build-essential

COPY . ./service

RUN pip3 install --no-cache-dir --upgrade -r ./service/requirements.txt

EXPOSE 9090

CMD python3 -m ${MAIN_MODULE:-service.main}


