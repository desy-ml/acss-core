FROM arm64v8/openjdk:8u201-jdk-alpine

#Install additional packages
RUN apk add --no-cache unzip wget supervisor openssh-server bash

EXPOSE 22

ENV ZOOKEEPER_VERSION 3.7.1

#Download Zookeeper bin
RUN wget http://mirror.vorboss.net/apache/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz && \
wget https://downloads.apache.org/zookeeper/KEYS && \
wget https://downloads.apache.org/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz.asc && \
wget https://downloads.apache.org/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz.sha512

#Verify download
RUN apk add --no-cache gnupg
RUN sha1sum apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz.sha512 && \
gpg --import KEYS && \
gpg --verify apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz.asc

#Generate Hostkeys
RUN /usr/bin/ssh-keygen -A

#Install
RUN tar -xzf apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz -C /opt

#Configure
RUN mv /opt/apache-zookeeper-${ZOOKEEPER_VERSION}-bin/conf/zoo_sample.cfg /opt/apache-zookeeper-${ZOOKEEPER_VERSION}-bin/conf/zoo.cfg

ENV JAVA_HOME usr/lib/jvm/java-1.8-openjdk
ENV ZK_HOME /opt/apache-zookeeper-${ZOOKEEPER_VERSION}-bin
RUN sed  -i "s|/tmp/zookeeper|$ZK_HOME/data|g" $ZK_HOME/conf/zoo.cfg; mkdir $ZK_HOME/data

EXPOSE 2181 2888 3888

WORKDIR /opt/apache-zookeeper-${ZOOKEEPER_VERSION}-bin
VOLUME ["/opt/apache-zookeeper-${ZOOKEEPER_VERSION}-bin/conf", "/opt/apache-zookeeper-${ZOOKEEPER_VERSION}-bin/data"]

# enable log4j.appender.ROLLINGFILE.MaxBackupIndex
RUN sed -i -r 's|#(log4j.appender.ROLLINGFILE.MaxBackupIndex.*)|\1|g' $ZK_HOME/conf/log4j.properties
# enbable autopurge
RUN sed -i -r 's|#autopurge|autopurge|g' $ZK_HOME/conf/zoo.cfg

CMD /usr/sbin/sshd && bash /opt/apache-zookeeper-${ZOOKEEPER_VERSION}-bin/bin/zkServer.sh start-foreground