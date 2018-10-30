FROM python:3.7-slim

CMD ["python", "appcode.py"]

WORKDIR /app

ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

ENV NAME World

