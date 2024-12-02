FROM python:3.12-alpine

WORKDIR /code
COPY ./requirements.txt /tmp
RUN apk add curl
RUN pip3 install --no-cache-dir --upgrade -r /tmp/requirements.txt
COPY . ./service
EXPOSE 9090

CMD python3 -m ${MAIN_MODULE:-service.main}
