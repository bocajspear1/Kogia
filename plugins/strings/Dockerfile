FROM alpine:3.22

RUN apk add -U  binutils

COPY run.sh /opt/run.sh

RUN chmod +x /opt/run.sh

ENTRYPOINT ["/opt/run.sh"]