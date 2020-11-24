FROM python:3.9
RUN apt update
RUN apt install -y locales locales-all

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

WORKDIR /
COPY requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY src /src

ENTRYPOINT ["python", "/src/run.py"]
