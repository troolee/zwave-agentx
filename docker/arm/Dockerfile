FROM alidron/rpi-python-openzwave:master
MAINTAINER Pavel Reznikov <pashka.reznikov@gmail.com>

RUN apt-get update && apt-get install -y  --force-yes \
    git

RUN pip install --no-cache-dir \
    docopt \
    git+https://github.com/rayed/pyagentx.git \
    git+https://github.com/11craft/louie.git

RUN apt-get remove -y --force-yes && apt-get autoremove -y --force-yes
