FROM alpine:3.15

RUN apk add -U file pev coreutils

RUN mkdir -p /usr/local/lib/pev && ln -s /usr/lib/pev/plugins /usr/local/lib/pev/plugins
RUN ls -la /usr/local/lib/pev/plugins

COPY run.sh /opt/run.sh
RUN chmod +x /opt/run.sh

ENTRYPOINT ["/opt/run.sh"]