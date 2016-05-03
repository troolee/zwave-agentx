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
from louie import dispatcher
import pyagentx
import subprocess
import os
import time
import datetime
from docopt import docopt
import logging
import traceback
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
from pprint import pprint
import re


VERSION = '0.2'
BETA = True

ROOT_OID = '1.3.6.1.4.1.47015'

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# ch.setFormatter(formatter)
logger.addHandler(ch)


ROOT = os.path.abspath(os.path.dirname(__file__))

rev = subprocess.check_output(['git', 'show', '-s', '--format=%ci', 'HEAD'], cwd=ROOT)[:10].decode('utf-8')
d = datetime.datetime.strptime(rev, '%Y-%m-%d') - datetime.datetime(2015, 8, 1)
VERSION = '.'.join(VERSION.split('.') + [str(d.days)])
if BETA:
    VERSION += ' beta'


def get_oid(oid):
    return '{}.{}'.format(ROOT_OID, oid)


zwave_nodes = None
zwave_sensors = {
    'temperature': {},
    'ultraviolet': {},
    'luminance': {},
    'humidity': {},
}


class ZeyeAgent(pyagentx.Agent):
    def setup(self):
        self.register(get_oid('2'), ZeyeInfoUpdater)
        self.register(get_oid('3.1'), ZeyeZwaveNodesUpdater)
        self.register(get_oid('3.2.1'), ZeyeZwaveTemperatureSensorsUpdater)
        self.register(get_oid('3.2.2'), ZeyeZwaveUltravioletSensorsUpdater)
        self.register(get_oid('3.2.3'), ZeyeZwaveLuminanceSensorsUpdater)
        self.register(get_oid('3.2.4'), ZeyeZwaveHumiditySensorsUpdater)


class ZeyeInfoUpdater(pyagentx.Updater):
    def update(self):
        self.set_OCTETSTRING('1.0', VERSION)


class ZeyeZwaveNodesUpdater(pyagentx.Updater):
    def _get_oid(self, index, field_index):
        return '2.1.{}.{}'.format(field_index, index)

    def update(self):
        global zwave_nodes

        if zwave_nodes is None:
            return

        self.set_INTEGER('1.0', len(zwave_nodes))
        for i in range(len(zwave_nodes)):
            n = zwave_nodes[i]
            self.set_INTEGER(self._get_oid(i, 1), i)
            self.set_INTEGER(self._get_oid(i, 2), n['zwaveNodeId'])
            self.set_OCTETSTRING(self._get_oid(i, 3), n['zwaveNodeName'])
            self.set_OCTETSTRING(self._get_oid(i, 4), n['zwaveNodeLocation'])
            self.set_INTEGER(self._get_oid(i, 5), n['zwaveNodeBaud'])
            self.set_INTEGER(self._get_oid(i, 6), n['zwaveNodeBattery'])
            self.set_INTEGER(self._get_oid(i, 7), n['zwaveNodeAwaked'])
            self.set_OCTETSTRING(self._get_oid(i, 8), n['zwaveNodeType'])
            self.set_OCTETSTRING(self._get_oid(i, 9), n['zwaveNodeTypeName'])


class ZeyeZwaveTemperatureSensorsUpdater(pyagentx.Updater):
    def _get_oid(self, index, field_index):
        return '2.1.{}.{}'.format(field_index, index)

    def update(self):
        global zwave_sensors

        if not zwave_sensors.get('temperature'):
            return

        sensors = sorted(zwave_sensors['temperature'].values(),
                         key=lambda x: x['zwaveTemperatureSensorNodeId'] * 10 + x['_sensorIndex'])

        self.set_INTEGER('1.0', len(sensors))
        for i in range(len(sensors)):
            n = sensors[i]
            self.set_INTEGER(self._get_oid(i, 1), i)
            self.set_INTEGER(self._get_oid(i, 2), n['zwaveTemperatureSensorNodeId'])
            self.set_OCTETSTRING(self._get_oid(i, 3), n['zwaveTemperatureSensorId'])
            self.set_OCTETSTRING(self._get_oid(i, 4), n['zwaveTemperatureSensorName'])
            self.set_OCTETSTRING(self._get_oid(i, 5), n['zwaveTemperatureSensorLocation'])
            self.set_INTEGER(self._get_oid(i, 6), n['zwaveTemperatureSensorValue'])


class ZeyeZwaveUltravioletSensorsUpdater(pyagentx.Updater):
    def _get_oid(self, index, field_index):
        return '2.1.{}.{}'.format(field_index, index)

    def update(self):
        global zwave_sensors

        if not zwave_sensors.get('ultraviolet'):
            return

        sensors = sorted(zwave_sensors['ultraviolet'].values(),
                         key=lambda x: x['zwaveUltravioletSensorNodeId'] * 10 + x['_sensorIndex'])

        self.set_INTEGER('1.0', len(sensors))
        for i in range(len(sensors)):
            n = sensors[i]
            self.set_INTEGER(self._get_oid(i, 1), i)
            self.set_INTEGER(self._get_oid(i, 2), n['zwaveUltravioletSensorNodeId'])
            self.set_OCTETSTRING(self._get_oid(i, 3), n['zwaveUltravioletSensorId'])
            self.set_OCTETSTRING(self._get_oid(i, 4), n['zwaveUltravioletSensorName'])
            self.set_OCTETSTRING(self._get_oid(i, 5), n['zwaveUltravioletSensorLocation'])
            self.set_INTEGER(self._get_oid(i, 6), n['zwaveUltravioletSensorValue'])


class ZeyeZwaveLuminanceSensorsUpdater(pyagentx.Updater):
    def _get_oid(self, index, field_index):
        return '2.1.{}.{}'.format(field_index, index)

    def update(self):
        global zwave_sensors

        if not zwave_sensors.get('luminance'):
            return

        sensors = sorted(zwave_sensors['luminance'].values(),
                         key=lambda x: x['zwaveLuminanceSensorNodeId'] * 10 + x['_sensorIndex'])

        self.set_INTEGER('1.0', len(sensors))
        for i in range(len(sensors)):
            n = sensors[i]
            self.set_INTEGER(self._get_oid(i, 1), i)
            self.set_INTEGER(self._get_oid(i, 2), n['zwaveLuminanceSensorNodeId'])
            self.set_OCTETSTRING(self._get_oid(i, 3), n['zwaveLuminanceSensorId'])
            self.set_OCTETSTRING(self._get_oid(i, 4), n['zwaveLuminanceSensorName'])
            self.set_OCTETSTRING(self._get_oid(i, 5), n['zwaveLuminanceSensorLocation'])
            self.set_INTEGER(self._get_oid(i, 6), n['zwaveLuminanceSensorValue'])


class ZeyeZwaveHumiditySensorsUpdater(pyagentx.Updater):
    def _get_oid(self, index, field_index):
        return '2.1.{}.{}'.format(field_index, index)

    def update(self):
        global zwave_sensors

        if not zwave_sensors.get('humidity'):
            return

        sensors = sorted(zwave_sensors['humidity'].values(),
                         key=lambda x: x['zwaveHumiditySensorNodeId'] * 10 + x['_sensorIndex'])

        self.set_INTEGER('1.0', len(sensors))
        for i in range(len(sensors)):
            n = sensors[i]
            self.set_INTEGER(self._get_oid(i, 1), i)
            self.set_INTEGER(self._get_oid(i, 2), n['zwaveHumiditySensorNodeId'])
            self.set_OCTETSTRING(self._get_oid(i, 3), n['zwaveHumiditySensorId'])
            self.set_OCTETSTRING(self._get_oid(i, 4), n['zwaveHumiditySensorName'])
            self.set_OCTETSTRING(self._get_oid(i, 5), n['zwaveHumiditySensorLocation'])
            self.set_INTEGER(self._get_oid(i, 6), n['zwaveHumiditySensorValue'])


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


def zwave_network_started(network):
    print("Z-wave network started: HomeId {:08x}".format(network.home_id))


def zwave_network_failed(network):
    print('Z-wave network FAILED.')


def zwave_read_nodes(network):
    global zwave_nodes
    nodes = sorted(network.nodes.values(), key=lambda x: x.node_id)
    zwave_nodes = [{
        'zwaveNodeId': n.node_id,
        'zwaveNodeName': n.product_name,
        'zwaveNodeLocation': n.location,
        'zwaveNodeBaud': n.max_baud_rate,
        'zwaveNodeBattery': n.get_battery_level() if n.get_battery_level() is not None else -1,
        'zwaveNodeAwaked': n.is_awake,
        'zwaveNodeType': n.product_type,
        'zwaveNodeTypeName': n.type,
    } for n in nodes]
    for node in nodes:
        zwave_read_values(network, node, node.values.values())


def zwave_read_values(network, node, values):
    for value in values:
        if value.genre != 'User':
            continue

        if re.search('Temperature', value.label, re.I):
            v = value.data
            if value.units == 'F':
                v = (v - 32) * 5 / 9
            v = int(100 * v)
            zwave_sensors['temperature'][value.value_id] = {
                'zwaveTemperatureSensorNodeId': node.node_id,
                'zwaveTemperatureSensorId': str(value.value_id),
                'zwaveTemperatureSensorName': value.label,
                'zwaveTemperatureSensorLocation': node.location,
                'zwaveTemperatureSensorValue': v,
                '_sensorIndex': value.index,
            }
        elif re.search('Ultraviolet', value.label, re.I):
            v = value.data
            v = int(100 * v)
            zwave_sensors['ultraviolet'][value.value_id] = {
                'zwaveUltravioletSensorNodeId': node.node_id,
                'zwaveUltravioletSensorId': str(value.value_id),
                'zwaveUltravioletSensorName': value.label,
                'zwaveUltravioletSensorLocation': node.location,
                'zwaveUltravioletSensorValue': v,
                '_sensorIndex': value.index,
            }
        elif re.search('Luminance', value.label, re.I):
            v = value.data
            v = int(100 * v)
            zwave_sensors['luminance'][value.value_id] = {
                'zwaveLuminanceSensorNodeId': node.node_id,
                'zwaveLuminanceSensorId': str(value.value_id),
                'zwaveLuminanceSensorName': value.label,
                'zwaveLuminanceSensorLocation': node.location,
                'zwaveLuminanceSensorValue': v,
                '_sensorIndex': value.index,
            }
        elif re.search('Humidity', value.label, re.I):
            v = value.data
            v = int(100 * v)
            zwave_sensors['humidity'][value.value_id] = {
                'zwaveHumiditySensorNodeId': node.node_id,
                'zwaveHumiditySensorId': str(value.value_id),
                'zwaveHumiditySensorName': value.label,
                'zwaveHumiditySensorLocation': node.location,
                'zwaveHumiditySensorValue': v,
                '_sensorIndex': value.index,
            }
        print(value)


def zwave_network_ready(network):
    print("Z-wave network ready: HomeId {:08x}, {} nodes found.".format(network.home_id, network.nodes_count))
    dispatcher.connect(zwave_value_update, ZWaveNetwork.SIGNAL_VALUE)
    dispatcher.connect(zwave_read_nodes, ZWaveNetwork.SIGNAL_NODE_ADDED)
    dispatcher.connect(zwave_read_nodes, ZWaveNetwork.SIGNAL_NODE_EVENT)
    dispatcher.connect(zwave_read_nodes, ZWaveNetwork.SIGNAL_NODE_REMOVED)
    zwave_read_nodes(network)


def zwave_value_update(network, node, value):
    print("Z-wave Value Update: Node: {} Value: {}.".format(node, value))
    zwave_read_values(network, node, [value])


def init_zwave_network(device=None, config_path=None, debug=False):
    options = ZWaveOption(device, config_path=config_path, user_path=".", cmd_line="")
    options.set_log_file("OZW_Log.log")
    options.set_append_log_file(False)
    options.set_console_output(False)
    options.set_save_log_level('Info')  # ('Info' if debug else 'Warning')
    options.set_logging(True)
    options.lock()

    zwave_network = ZWaveNetwork(options, autostart=False)

    # We connect to the louie dispatcher
    dispatcher.connect(zwave_network_started, ZWaveNetwork.SIGNAL_NETWORK_STARTED)
    dispatcher.connect(zwave_network_failed, ZWaveNetwork.SIGNAL_NETWORK_FAILED)
    dispatcher.connect(zwave_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

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
