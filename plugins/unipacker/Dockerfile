FROM alpine:3.15

WORKDIR /
RUN apk add -U --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing yara
RUN apk add -U --no-cache python2 python3 python3-dev build-base linux-headers capstone-dev
RUN python3 -m ensurepip && pip3 install --upgrade pip wheel
RUN pip3 install unipacker

COPY run.sh /opt/run.sh
RUN chmod +x /opt/run.sh
ENTRYPOINT ["/opt/run.sh"]