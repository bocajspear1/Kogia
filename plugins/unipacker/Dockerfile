FROM alpine:3.13

WORKDIR /

RUN apk add -U --no-cache wget python2 python3 python3-dev build-base linux-headers capstone-dev openssl-dev unzip
RUN python3 -m ensurepip && pip3 install --upgrade pip wheel
RUN pip3 install unipacker

COPY run.sh /opt/run.sh
RUN chmod +x /opt/run.sh
ENTRYPOINT ["/opt/run.sh"]