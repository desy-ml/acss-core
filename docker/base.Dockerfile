FROM python:3.8-slim-buster AS build


RUN apt-get update

RUN apt-get install -y build-essential
RUN apt-get install -y git

# Build librdkafka
RUN cd /opt/ && git clone https://github.com/edenhill/librdkafka.git && cd librdkafka && ./configure && make && make install

FROM python:3.8-slim-buster

ENV PIP_NO_CACHE_DIR=off

COPY --from=build /usr/local/lib/pkgconfig /usr/local/lib/pkgconfig
COPY --from=build /usr/local/lib/librdkafka* /usr/local/lib/
COPY --from=build /usr/local/include/librdkafka* /usr/local/include/librdkafka
ENV LD_LIBRARY_PATH=/usr/local/lib/:${LD_LIBRARY_PATH}
ENV C_INCLUDE_PATH=/usr/local/include/
ENV CPLUS_INCLUDE_PATH=/usr/local/include/



