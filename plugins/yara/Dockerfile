FROM alpine:3.15

WORKDIR /
RUN apk add -U --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing yara
RUN apk add -U git 

COPY combine_rules.sh /opt/combine_rules.sh
RUN chmod +x /opt/combine_rules.sh

RUN mkdir /opt/combined
RUN git clone --depth 1 https://github.com/bartblaze/Yara-rules.git /opt/rules/bartblaze && \
    rm /opt/rules/bartblaze/rules/crimeware/RedLine_Campaign_June2021.yar
RUN /opt/combine_rules.sh /opt/rules/bartblaze /opt/combined/bartblaze.yar

# RUN git clone --depth 1 https://github.com/Neo23x0/signature-base.git /opt/rules/Neo23x0 && \
#     rm /opt/rules/Neo23x0/yara/generic_anomalies.yar && \
#     rm /opt/rules/Neo23x0/yara/general_cloaking.yar && \
#     rm /opt/rules/Neo23x0/yara/gen_webshells_ext_vars.yar && \
#     rm /opt/rules/Neo23x0/yara/thor_inverse_matches.yar && \
#     rm /opt/rules/Neo23x0/yara/yara_mixed_ext_vars.yar
# RUN /opt/combine_rules.sh /opt/rules/Neo23x0/ /opt/combined/Neo23x0.yar

RUN git clone --depth 1 https://github.com/eset/malware-ioc.git /opt/rules/eset
RUN /opt/combine_rules.sh /opt/rules/eset /opt/combined/eset.yar

RUN git clone --depth 1 https://github.com/kevoreilly/CAPEv2.git /opt/rules/cape 
RUN /opt/combine_rules.sh /opt/rules/cape/data/yara /opt/combined/capev2.yar

RUN git clone --depth 1 https://github.com/malpedia/signator-rules.git /opt/rules/malpedia 
RUN /opt/combine_rules.sh /opt/rules/malpedia /opt/combined/malpedia.yar

# RUN git clone --depth 1 https://github.com/mikesxrs/Open-Source-YARA-rules.git /opt/rules/mikesxrs 
# RUN /opt/combine_rules.sh /opt/rules/mikesxrs /opt/combined/mikesxrs.yar

RUN yara -D -m /opt/combined/bartblaze.yar \
    #  /opt/combined/Neo23x0.yar \
     /opt/combined/eset.yar \
     /opt/combined/capev2.yar \
     /opt/combined/malpedia.yar \
    #  /opt/combined/mikesxrs.yar \
     /bin/ls

COPY run.sh /opt/run.sh
RUN chmod +x /opt/run.sh

ENTRYPOINT ["/opt/run.sh"]