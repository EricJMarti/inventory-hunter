FROM python:3.9
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src /src
ENTRYPOINT ["python", "/src/run.py"]
