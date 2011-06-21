#!/usr/bin/env python

from optparse import OptionParser
import json
import sys
import urllib2

# Nagios Exit Statuses
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

def getJSONRabbitMQStatus(username, password, server_ip, port, api_path):
    """Returns a the json for request at the queue server /api/<api_path>
    """

    BASE_URL = 'http://{0}:{1}'.format(server_ip, port)
    API_URL = 'http://{0}:{1}/api/{2}'.format(server_ip, port, api_path)

    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, BASE_URL, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)

    response = json.loads(urllib2.urlopen(API_URL).read())

    # Serialize the response and return it
    return json.dumps(response)

from pprint import pprint

def main():
    parser = OptionParser()
    parser.add_option('-u', '--username', dest='username')
    parser.add_option('-p', '--password', dest='password')
    parser.add_option('-H', '--hostname', dest='server_ip')
    parser.add_option('-I', '--server-ip', dest='server_ip')

    # Doesn't do anything just for nagios plugin spec
    # parser.add_option('-v', '--verbose', dest='verbosity')
    parser.add_option('--port', dest='port')
    parser.add_option('--api_path', dest='api_path')

    options, args = parser.parse_args()

    # Check for required options
    for option in ('username', 'password', 'server_ip', 'port', 'api_path'):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            exit(CRITICAL)

    result = json.loads(getJSONRabbitMQStatus(**options.__dict__))

    if not result:
        print >> sys.stdout, 'CRITICAL - JSON get failed'
        exit(CRITICAL)

    # If we got this far, let's tell Nagios the report is okay.
    sys.stdout.write('OK - {0} is up|'.format(options.api_path))

    api_path = options.api_path
    if api_path == 'overview':
        for k, v in result['queue_totals'].iteritems():
            sys.stdout.write('{0}={1}; '.format(k, v))


        message_stats = result['message_stats']
        for key in ('publish', 'ack', 'deliver'):
            rate = message_stats[key + '_details']['rate']
            sys.stdout.write('rate_{0}={1}; '.format(key, rate))

    elif api_path == 'queues':
        for queue in result:
            queue_name = queue['name']
            for key in ('messages', 'messages_ready', 'messages_unacknowledged'):
                s = '{0}_{1}={2}; '.format(queue_name, key, queue[key])
                sys.stdout.write(s)

    # pprint(result)

    sys.stdout.flush()
    exit(OK)

if __name__ == '__main__':
    main()
