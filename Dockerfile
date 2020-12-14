FROM python:3.9
RUN apt update
RUN apt install -y chromium chromium-driver locales locales-all

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

WORKDIR /
ARG requirements=requirements.txt
COPY $requirements /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY VERSION /src/version.txt
COPY pyproject.toml /src/pyproject.toml
COPY src /src

ENTRYPOINT ["bash", "/src/run.bash"]
