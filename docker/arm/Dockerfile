FROM hypriot/rpi-python:2.7
MAINTAINER Pavel Reznikov <pashka.reznikov@gmail.com>
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y  --force-yes \
    apt-utils \
    git \
    make
RUN pip install cython
RUN git clone https://github.com/OpenZWave/python-openzwave
WORKDIR /python-openzwave
RUN make repo-deps \
    && make update \
    && make build \
    && make install
RUN apt-get autoremove -y  --force-yes
WORKDIR /
