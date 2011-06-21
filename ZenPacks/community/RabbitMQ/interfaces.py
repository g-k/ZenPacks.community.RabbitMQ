
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t


class IRabbitMQMonitorDataSourceInfo(IRRDDataSourceInfo):

    port = schema.Int(title=_t(u'Port'), group=_t('RabbitMQ Monitor'))

    ipAddress = schema.Text(title=_t(u'Ip Address'), group=_t('RabbitMQ Monitor'))

    api_path = schema.Text(title=_t(u'API Path'), group=_t('RabbitMQ Monitor'))

    user = schema.Text(title=_t(u'User'), group=_t('RabbitMQ Monitor'))
    password = schema.Password(title=_t(u'Password'), group=_t('RabbitMQ Monitor'))

    cycletime = schema.Int(title=_t(u'Cycle Time (seconds)'))
