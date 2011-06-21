"""
RabbitQueueMap
gathers a list of rabbitmq queues over SNMP and adds
datasources, graphs, and datapoints for messages to the device.
"""

from Products.DataCollector.plugins.CollectorPlugin import \
     (SnmpPlugin, GetMap, GetTableMap)

# This is net-snmp specific
nsExtendObjects = ".1.3.6.1.4.1.8072.1.3.2"

# the name of our extend process in '.' joined ascii
oid_name = '.'.join([str(ord(char)) for char in 'check_rabbit'])

# Not sure what the 12 is for
oid_name = '.12.' + oid_name


# Test inputs

rabbit_up_input = \
"""WARNING: ignoring /etc/rabbitmq/rabbitmq.conf -- location has moved to /etc/rabbitmq/rabbitmq-env.conf
Listing queues ...
evo.workers.subscription_confirmation_mailing_generator.SubscriptionCreated 0 0 0
evo.workers.broadcast_cleanup.BroadcastMailingsCreated 0 0 0
...done.
"""

rabbit_down_input = \
"""WARNING: ignoring /etc/rabbitmq/rabbitmq.conf -- location has moved to /etc/rabbitmq/rabbitmq-env.conf
Listing queues ...
Error: unable to connect to node rabbit@queue: nodedown
diagnostics:
    - nodes and their ports on queue: [{rabbitmqctl7524,56280}]
    - current node: rabbitmqctl7524@queue
    - current node home dir: /var/lib/rabbitmq
    - current node cookie hash: bQ7kdgLDk+kHRhYEsgFxHA==
"""

def queue_lines(output_string):
    """parse rabbitmqctl output (like above) to get lines of queue data"""

    parsing = False

    for line in output_string.split('\n'):

        if parsing:
            if "...done." in line:
                print "Stopped parsing queue lines"
                raise StopIteration
            yield line

        elif "Listing queues ..."  in line:
            print "Started parsing queue lines"
            parsing = True


class RabbitQueueMap(SnmpPlugin):

    maptype = "RabbitQueueMap"

    # This magical attribute is required
    # though we don't have to pass it to GetMap
    columns = {
        nsExtendObjects + '.1.0' : 'extend_entries',

        # nsExtendConfigTable nsExtendConfigEntry
        nsExtendObjects + '.2.1.2' + oid_name : 'nsExtendCommand',
        nsExtendObjects + '.2.1.3' + oid_name : 'nsExtendArgs',
        nsExtendObjects + '.2.1.4' + oid_name : 'nsExtendInput',
        nsExtendObjects + '.2.1.5' + oid_name : 'nsExtendCacheTime',
        nsExtendObjects + '.2.1.6' + oid_name : 'nsExtendExecType',
        nsExtendObjects + '.2.1.7' + oid_name : 'nsExtendRunType',
        nsExtendObjects + '.2.1.20' + oid_name : 'nsExtendStorage',
        nsExtendObjects + '.2.1.21' + oid_name : 'nsExtendStatus',

        # nsExtendOutput1Table nsExtendOutput1Entry
        nsExtendObjects + '.3.1.1' + oid_name : 'nsExtendOutput1Line',
        nsExtendObjects + '.3.1.2' + oid_name : 'nsExtendOutputFull',
        nsExtendObjects + '.3.1.3' + oid_name : 'nsExtendOutNumLines',
        nsExtendObjects + '.3.1.4' + oid_name : 'nsExtendResult',
        }

    snmpGetMap = GetMap(columns)

    def process(self, device, results, log):
        """collect snmp information from this device"""

        log.info('\nprocessing {0} for device {1}\n'.format(self.name(), device.id))

        # Results of snmpGetMap and snmpGetTableMaps
        getdata, tabledata = results

        log.info('======= RESULTS ======')
        log.info('\ngetdata:\n{0}\ntabledata:\n{1}'.format(getdata, tabledata))

        # Check command exit status
        if getdata['nsExtendResult'] != 0:
            log.error("The extend command exited with a non zero status.")
            return None

        args = getdata['nsExtendArgs'].split()

        # Make sure we're getting queue data
        if not len(args) or args[0] != 'list_queues':
            log.error("Cannot get queue data without listing queues.")
            return None

        # Make sure we're getting queue names
        if not 'name' in args:
            log.error("Cannot update queue mapping without queue names.")
            return None


        data_args = args[1:] # args we collect data on
        num_data_args = len(data_args)

        queues = []
        for line in queue_lines(getdata['nsExtendOutputFull']):

            data_points = line.split('\t')

            if len(data_points) != num_data_args:
                log.warn('Skipping line with the wrong number of args.')
                log.warn(line)
                continue

            queue = dict(zip(data_args, data_points))
            queues.append(queue)
            log.info("Got queue: {0}".format(queue))

        log.info(device)
        log.info(type(device))

        # om = self.objectMap(getdata)

        # # allow for custom parse of DeviceMap data
        # scDeviceMapParse = getattr(device, 'scDeviceMapParse', None)
        # if scDeviceMapParse:
        #     om = scDeviceMapParse(device, om)

        return None
