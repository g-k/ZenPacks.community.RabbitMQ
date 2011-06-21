
from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from ZenPacks.community.RabbitMQ.interfaces import IRabbitMQMonitorDataSourceInfo
from ZenPacks.community.RabbitMQ.datasources.RabbitMQDataSource import RabbitMQMonitorDataSource

class RabbitMQMonitorDataSourceInfo(RRDDataSourceInfo):

    implements(IRabbitMQMonitorDataSourceInfo)

    ipAddress = ProxyProperty('ipAddress')

    port = ProxyProperty('port')
    api_path = ProxyProperty('api_path')

    user = ProxyProperty('user')
    password = ProxyProperty('password')

    @property
    def testable(self):
        """
        We can NOT test this datsource against a specific device
        """
        return False
