FROM python:3.12-alpine
WORKDIR /code/service
COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade -r /code/requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:/code/service"
COPY libs /code/service/libs
COPY routers /code/service/routers
COPY config.yml main.py /code/service/
EXPOSE 9290
CMD ["python3", "-u", "main.py"]
