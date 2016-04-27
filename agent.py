#!/usr/bin/env python
"""Zeye Agent

Usage:
    agent.py [-dD] run [--device=<device>] [--config=<config>]
    agent.py (-h | --help)
    agent.py (-v | --version)

Options:
    -h --help           Show this screen.
    -v --version        Show version.
    --device=<device>   SNMP controller device [default: /dev/ttyUSB0].
    --config=<config>   OpenZWave config path [default: ./config]
    -d --debug          Show debug output.
    -D --full-debug     Show debug and pyagentx debug output.
"""
import pyagentx
import subprocess
import os
import datetime
from docopt import docopt
import logging
import traceback
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption


VERSION = '0.2'
BETA = True

ROOT_OID = '1.3.6.1.4.1.47015'

logger = logging.getLogger(__name__)

ROOT = os.path.abspath(os.path.dirname(__file__))

rev = subprocess.check_output(['git', 'show', '-s', '--format=%ci', 'HEAD'], cwd=ROOT)[:10].decode('utf-8')
d = datetime.datetime.strptime(rev, '%Y-%m-%d') - datetime.datetime(2015, 8, 1)
VERSION = '.'.join(VERSION.split('.') + [str(d.days)])
if BETA:
    VERSION += ' beta'


def get_oid(oid):
    return '{}.{}'.format(ROOT_OID, oid)


class ZeyeAgent(pyagentx.Agent):
    def setup(self):
        self.register(get_oid('2'), ZeyeInfoUpdater)
        self.register(get_oid('3.1'), ZeyeZwaveNodesUpdater)


class ZeyeInfoUpdater(pyagentx.Updater):
    def update(self):
        self.set_OCTETSTRING('1.0', VERSION)


class ZeyeZwaveNodesUpdater(pyagentx.Updater):
    def _get_oid(self, index, field_index):
        return '2.1.{}.{}'.format(field_index, index)

    def update(self):
        self.set_INTEGER('1.0', 3)  # zwaveNodesCount
        for i in range(1, 4):
            self.set_INTEGER(self._get_oid(i, 1), i)                           # zwaveNodeIndex
            self.set_INTEGER(self._get_oid(i, 2), i)                           # zwaveNodeId
            self.set_OCTETSTRING(self._get_oid(i, 3), 'Node {}'.format(i))     # zwaveNodeName
            self.set_OCTETSTRING(self._get_oid(i, 4), '')                      # zwaveNodeLocation
            self.set_INTEGER(self._get_oid(i, 5), 4000)                        # zwaveNodeBaud
            self.set_INTEGER(self._get_oid(i, 6), 100)                         # zwaveNodeBattery
            self.set_INTEGER(self._get_oid(i, 7), 2)                           # zwaveNodeAwaked


def init_loggers(debug=False, pyagentx_debug=False):
    level = logging.DEBUG if pyagentx_debug else logging.INFO if debug else logging.WARNING
    pyagentx_logger = logging.getLogger('pyagentx')
    pyagentx_logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    pyagentx_logger.addHandler(ch)
    return pyagentx_logger


def init_zwave_network(device=None, config_path=None, debug=False):
    options = ZWaveOption(device, config_path=config_path, user_path=".", cmd_line="")
    options.set_log_file("OZW_Log.log")
    options.set_append_log_file(False)
    options.set_console_output(True)
    options.set_save_log_level('Debug' if debug else 'Info')
    options.set_logging(False)
    options.lock()

    zwave_network = ZWaveNetwork(options, autostart=False)
    return zwave_network


def start_agent(device=None, config_path=None, debug=False, pyagentx_debug=False):
    init_loggers(debug, pyagentx_debug)

    zwave_network = init_zwave_network(device, config_path, debug)

    while True:
        try:
            zwave_network.start()
            agent = ZeyeAgent()
            agent.start()
        except KeyboardInterrupt:
            agent.stop()
            zwave_network.stop()
            exit(0)
        except Exception:
            logger.error('Unhandled error:')
            logger.error(traceback.format_exc())
            try:
                agent.stop()
                zwave_network.stop()
            except Exception:
                pass
            logger.debug('Restarting in 3 sec...')
            import time
            time.sleep(3)


if __name__ == '__main__':
    arguments = docopt(__doc__)

    if arguments['--version']:
        print('Version: {}'.format(VERSION))
        exit(0)

    if arguments['run']:
        start_agent(
            device=arguments['--device'],
            config_path=arguments['--config'],
            debug=arguments['--debug'] or arguments['--full-debug'],
            pyagentx_debug=arguments['--full-debug'])
