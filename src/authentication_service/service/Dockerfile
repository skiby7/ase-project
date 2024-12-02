FROM python:3.12-alpine

WORKDIR /code

COPY . ./service

RUN pip3 install --no-cache-dir --upgrade -r ./service/requirements.txt

EXPOSE 9090

CMD python3 -m ${MAIN_MODULE:-service.main}
