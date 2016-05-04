FROM alidron/rpi-python-openzwave:master
MAINTAINER Pavel Reznikov <pashka.reznikov@gmail.com>

RUN apt-get update && apt-get install -y  --force-yes \
    git

RUN rm -rf /tmp/*

COPY requirements.txt /
RUN pip install -Ur /requirements.txt

RUN apt-get remove -y --force-yes && apt-get autoremove -y --force-yes && rm /requirements.txt
