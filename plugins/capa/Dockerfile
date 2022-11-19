FROM ubuntu:20.04

RUN apt-get -qq update \
&& DEBIAN_FRONTEND="noninteractive" apt-get -q install -y curl unzip

RUN curl $(curl -s https://api.github.com/repos/mandiant/capa/releases/latest | grep -o -- 'https://.*linux.zip') --output /tmp/capa.zip -L

RUN cd /tmp && unzip capa.zip && mv capa /usr/bin/capa

RUN chmod +x /usr/bin/capa

COPY run.sh /opt/run.sh

RUN chmod +x /opt/run.sh

ENTRYPOINT ["/opt/run.sh"]
