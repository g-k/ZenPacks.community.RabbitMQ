'''RabbitMQDataSource.py'''

import Products.ZenModel.RRDDataSource as RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from AccessControl import ClassSecurityInfo, Permissions
from Products.ZenUtils.ZenTales import talesCompile, getEngine
from Products.ZenUtils.Utils import binPath


class RabbitMQDataSource(ZenPackPersistence, RRDDataSource.RRDDataSource):

    MONITOR = 'RabbitMQMonitor'
    ZENPACKID = 'ZenPacks.community.RabbitMQ'

    sourcetypes = (MONITOR,)
    sourcetype = MONITOR

    eventClass = '/Unknown'

    ipAddress = '${dev/manageIp}'

    rabbit_port = 55672

    user = 'guest'
    password = 'guest'

    api_path = 'overview'

    _properties = RRDDataSource.RRDDataSource._properties + (
        {'id':'ipAddress', 'type':'string', 'mode':'w'},

        {'id':'rabbit_port', 'type':'int', 'mode':'w'},

        {'id':'user', 'type':'string', 'mode':'w'},
        {'id':'password', 'type':'string', 'mode':'w'},

        {'id':'api_path', 'type':'string', 'mode':'w'},

        )

    _relations = RRDDataSource.RRDDataSource._relations + ()

    factory_type_information = (
        {
            'immediate_view' : 'editRabbitMQMonitorDataSource',
            'actions'        :
            (
                {
                    'id'            : 'edit',
                    'name'          : 'Data Source',
                    'action'        : 'editRabbitMQMonitorDataSource',
                    'permissions'   : ( Permissions.view, ),
                    },
                )
            },
        )

    security = ClassSecurityInfo()

    def __init__(self, id, title=None, buildRelations=True):
        RRDDataSource.RRDDataSource.__init__(self, id, title, buildRelations)

    def getDescription(self):
        if self.sourcetype == self.MONITOR:
            return 'http://{0}:{1}/api/{2}'.format(self.ipAddress,
                                                   self.rabbit_port, self.api_path)

        return RRDDataSource.RRDDataSource.getDescription(self)

    def useZenCommand(self):
        return True

    def getCommand(self, context):
        parts = [ 'check_rabbitmq.py' ]

        if self.ipAddress:
            parts.append('-I %s' % self.ipAddress)

        if self.rabbit_port:
            parts.append('--port %s' % self.rabbit_port)

        if self.user:
            parts.append('-u {0}'.format(self.user))
        if self.password:
            parts.append('-p %s' % self.password )

        if self.api_path:
            parts.append('--api_path %s' % self.api_path)

        cmd = ' '.join(parts)
        cmd = RRDDataSource.RRDDataSource.getCommand(self, context, cmd)
        return cmd

    def checkCommandPrefix(self, context, cmd):
        zp = self.getZenPack(context)
        return zp.path('libexec', cmd)

    def addDataPoints(self):
        if not self.datapoints._getOb('messages', None):
            self.manage_addRRDDataPoint('messages')

    def zmanage_editProperties(self, REQUEST=None):
        '''validation, etc'''
        if REQUEST:
            # ensure default datapoint didn't go away
            self.addDataPoints()
            # and eventClass
            if not REQUEST.form.get('eventClass', None):
                REQUEST.form['eventClass'] = self.__class__.eventClass
        return RRDDataSource.RRDDataSource.zmanage_editProperties(self, REQUEST)
