FROM ubuntu:latest
RUN apt-get update

# Install conda
RUN apt-get install -y wget
RUN apt-get install -y git
RUN apt-get install -y build-essential

RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh -O /opt/miniforge.sh
RUN chmod +x /opt/miniforge.sh
RUN ./opt/miniforge.sh -b -p /opt/miniforge

RUN cd /opt/ && git clone https://github.com/edenhill/librdkafka.git && cd librdkafka && ./configure && make && make install


RUN mkdir -p /src
COPY environment.yml /src/

RUN /opt/miniforge/bin/conda env create --file /src/environment.yml

RUN /opt/miniforge/envs/pipe_env/bin/python -m pip install confluent-kafka

RUN apt-get install -y kafkacat net-tools iputils-ping
