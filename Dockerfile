FROM python:3.10

ENV PYTHONPATH /usr/src/app

ADD . .

RUN apt update && apt --no-install-recommends -y install build-essential

RUN pip install --upgrade pip wheel \
	&& pip install --upgrade pytest-rerunfailures \
	&& pip install --no-cache-dir -Ur requirements.txt
