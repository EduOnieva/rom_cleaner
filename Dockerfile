FROM python:3.12.4-slim-bullseye

RUN apt-get -y update

COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

COPY ./src /rom_cleaner
COPY constants.py /rom_cleaner/constants.py

ENTRYPOINT ["python", "rom_cleaner"]