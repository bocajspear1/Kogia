FROM ubuntu:20.04 as builder

RUN dpkg --add-architecture i386

RUN apt-get -qq update \
&& DEBIAN_FRONTEND="noninteractive" apt-get -q install -y make upx-ucl wget unzip wine64 wine32

WORKDIR /opt

RUN wget https://github.com/EgeBalci/amber/releases/download/v3.1/amber_linux_amd64_3.1.zip && unzip amber_linux_amd64_3.1.zip 
RUN mv amber_linux_amd64_3.1 amber

RUN wget 'https://www.autoitscript.com/cgi-bin/getfile.pl?autoit3/autoit-v3.zip' -O autoit-v3.zip && unzip autoit-v3.zip
RUN wine hostname
RUN mv install ~/.wine/drive_c/autoit

COPY ./test.x86-64.exe .
COPY ./test.x86.exe .

RUN apt-get -qq update \
&& DEBIAN_FRONTEND="noninteractive" apt-get -q install -y xvfb xserver-xspice

COPY Makefile .

RUN mkdir /tmp/out && make

COPY autoit.au3 .

RUN wget https://www.un4seen.com/files/petite24.zip -O petite.zip && unzip petite.zip 
RUN mv petite.exe ~/.wine/drive_c/petite.exe

COPY wine_run.sh .
RUN chmod +x /opt/wine_run.sh && /opt/wine_run.sh

FROM scratch as artifact
COPY --from=builder /tmp/out /out