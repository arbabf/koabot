# based on debian buster 
FROM python:3.9 

WORKDIR /koabot 

COPY requirements.txt requirements.txt 
COPY src/koabot/  . 

RUN pip3 install -r requirements.txt 

USER root 

ENTRYPOINT ["python3"]

CMD ["/koabot/koabot.py"]



