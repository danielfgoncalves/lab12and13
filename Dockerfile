FROM python:2.7

RUN apt-get update
RUN apt-get -y upgrade

RUN pip install boto

ADD /my_application /my_application
RUN pip install -r /my_application/req.txt
EXPOSE 5000
WORKDIR /my_application


CMD python boto-server.py
