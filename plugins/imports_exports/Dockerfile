FROM alpine:3.15

RUN apk add -U python3 py3-pip 
RUN pip3 install pyelftools pefile

COPY run.sh /opt/run.sh
COPY runner.py /opt/runner.py

RUN chmod +x /opt/run.sh

ENTRYPOINT ["/opt/run.sh"]