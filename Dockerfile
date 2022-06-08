FROM ubuntu:18.10

LABEL author="Shayan Hemmatiyan <shayan.hemmatiyan@gmail.com>"

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip

COPY . ./app
WORKDIR ./app

RUN pip3 install -r requirements.txt

EXPOSE 5000
CMD python3 app.py run -h 0.0.0.0 -p 5000
