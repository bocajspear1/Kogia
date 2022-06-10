FROM ubuntu:20.04 as builder

RUN apt-get -qq update \
&& DEBIAN_FRONTEND="noninteractive" apt-get -q install -y gnupg ca-certificates

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
RUN echo "deb https://download.mono-project.com/repo/ubuntu stable-focal main" | tee /etc/apt/sources.list.d/mono-official-stable.list
RUN apt-get -qq update \
&& DEBIAN_FRONTEND="noninteractive" apt-get -q install -y make mono-devel

WORKDIR /opt

COPY test.cs .
COPY Makefile .

RUN mkdir /tmp/out && make

FROM scratch as artifact
COPY --from=builder /tmp/out /out