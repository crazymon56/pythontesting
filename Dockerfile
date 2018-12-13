FROM python:3.6-slim

CMD ["python", "appcode.py"]

WORKDIR /app

ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt


EXPOSE 80
 
ENV LANG C.UTF-8  
ENV LANGUAGE C.UTF-8 
ENV LC_ALL C.UTF-8

