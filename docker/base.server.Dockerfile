FROM python:3.8-slim-buster AS build


RUN apt-get update

RUN apt-get install -y build-essential
RUN apt-get install -y git
RUN apt-get install -y curl

RUN curl -L "https://download.docker.com/linux/static/stable/$(uname -m)/docker-20.10.8.tgz" -o docker-20.10.8.tgz
RUN tar xzvf docker-20.10.8.tgz
RUN cp docker/* /usr/bin/
# Build librdkafka
RUN cd /opt/ && git clone https://github.com/edenhill/librdkafka.git && cd librdkafka && ./configure && make && make install

RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose


FROM python:3.8-slim-buster

ENV PIP_NO_CACHE_DIR=off

COPY --from=build /usr/local/lib/pkgconfig /usr/local/lib/pkgconfig
COPY --from=build /usr/local/lib/librdkafka* /usr/local/lib/
COPY --from=build /usr/local/bin/docker-compose /usr/local/bin/
COPY --from=build /usr/bin/docker /usr/bin/

RUN chmod +x /usr/local/bin/docker-compose

RUN ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

RUN mkdir -p /pipe
COPY Pipfile /pipe/
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pipenv
RUN cd pipe && mkdir .venv && pipenv install --dev