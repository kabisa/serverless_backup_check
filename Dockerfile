FROM frolvlad/alpine-python3:latest

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
COPY requirements_test.txt .
RUN pip install -r requirements_test.txt

COPY src src
COPY tests tests
RUN flake8 .
ENTRYPOINT ./tests/test.sh
