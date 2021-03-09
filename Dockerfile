FROM python:3.9
RUN apt update
RUN apt upgrade -y
RUN apt install -y chromium chromium-driver locales locales-all xvfb
RUN curl -fsSL https://deb.nodesource.com/setup_15.x | bash -
RUN apt install -y nodejs
RUN npm --prefix /src install puppeteer

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
