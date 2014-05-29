#-*- coding:utf-8 -*-

"""sslfetch.connections.py
 Python Lib for ssl connection downloads.

 Complete with:
    optional timestamp file to load
    Headers:
        'User-Agent'
        'If-Modified-Since',
        'last-modified'
        custom
    proxies

Copyright (C) 2013 Brian Dolbec <dolsen@gentoo.org>

Distributed under the terms of the GNU General Public License v2
 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 2 of the License.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

"""

import sys
import os

VERIFY_SSL = False
VERIFY_MSGS = []

import requests
from requests.exceptions import SSLError

# py3.2
if sys.hexversion >= 0x30200f0:
    VERIFY_SSL = True
else:
    try: # import and enable SNI support for py2
        from requests.packages.urllib3.contrib import pyopenssl
        pyopenssl.inject_into_urllib3()
        VERIFY_SSL = True
        VERIFY_MSGS = ["Successfully enabled ssl certificate verification."]
    except ImportError as e:
        VERIFY_MSGS = [
            "Failed to import and inject pyopenssl/SNI support into urllib3",
            "Disabling certificate verification",
            "Error was:" + e
        ]
        VERIFY_SSL = False


def fileopen(path, mode='r', enc="UTF-8"):
    """py2, py3 compatibility function"""
    try:
        f = open(path, mode, encoding=enc)
    except TypeError:
        f = open(path, mode)
    return f


class Connector(object):
    """Primary connection interface using the dev-python/requests package
    """

    def __init__(self, output_dict, proxies=None, useragent='ssl-fetch'):
        """Connector __init__()

        @param output_dict: dictionary of: eg: {
            'info': logging.info,    # function
            'error': logging.error,   # function
            'kwargs-info: {},  # dict for **kwargs use
            'kwargs-error': {} # dict for **kwargs use
            }
            all output will be called via the self.output() using:
            def output(self, mode, msg):
                kwargs = self.output_dict['kwargs-%s' % mode]
                func = self.output_dict[mode]
                func(msg, **kwargs)

            NOTE: logging module primarily uses the setLevel()
            so the kwargs-* parameters should be {}.
            For custom output modules, the kwargs-* variables can be set
            to whatever is needed to be passed to them.
            eg:
            'kwargs-info: {'level': 2},
        @param proxies: dictionary, default of None, it will try to
            get them from the environment.
        @param useragent: string, the User-Agent string to pass to the server,
            default of 'ssl-fetch' is just due to parameter ordering
        """
        self.output_dict = output_dict
        self.proxies = proxies or self.get_env_proxies()
        self.headers = {'Accept-Charset': 'utf-8',
            'User-Agent': useragent}

        # check if there were any initialization messages
        # and output them now that we have an output assigned
        if VERIFY_MSGS:
            for msg in VERIFY_MSGS:
                self.output('info', msg + '\n')


    def add_timestamp(self, headers, tpath=None, timestamp=None):
        """Adds an 'If-Modified-Since' header to the headers using
        the information supplied via a tpath file or timestamp.

        @param headers: dictionary, optional headers to use
        @param tpath: string, optional filepath to a timestamp file
                      to use in the headers
        @param timestamp: string, optional timestamp to use in the headers
        @rtype: dictionary of updated headers
        """
        if tpath and os.path.exists(tpath):
            with fileopen(tpath,'r') as previous:
                timestamp = previous.read()
        if timestamp:
            headers['If-Modified-Since'] = timestamp
            self.output('info', 'Current-modified: %s\n' % timestamp)
        return headers


    def connect_url(self, url, headers=None, tpath=None, timestamp=None):
        """Establishes a verified connection to the specified url

        @param url: string
        @param headers: dictionary, optional headers to use
        @param tpath: string, optional filepath to a timestamp file
                      to use in the headers
        @param timestamp: string, optional timestamp to use in the headers
        @rtype: request connection
        """

        if not headers:
            headers = self.headers

        if timestamp or tpath:
            self.add_timestamp(headers, tpath=tpath, timestamp=timestamp)

        verify = url.startswith('https') and VERIFY_SSL
        self.output('info', "Enabled ssl certificate verification: %s, for: %s\n"
            %(str(verify), url))

        self.output('info', 'Connector.connect_url(); headers = %s\n'
            %str(headers))
        self.output('info', 'Connector.connect_url(); connecting to opener\n')

        try:
            connection = requests.get(
                url,
                headers=headers,
                verify=verify,
                proxies=self.proxies,
                )
        except SSLError as error:
            self.output('error', 'Connector.connect_url(); Failed to update the '
                'mirror list from: %s\nSSLError was:%s\n'
                % (url, str(error)))
        except Exception as error:
            self.output('error', 'Connector.connect_url(); Failed to retrieve '
                'the content from: %s\nError was: %s\n'
                % (url, str(error)))

        self.output('info', 'Connector.connect_url() HEADERS = %s\n'
            %str(connection.headers))
        self.output('info', 'Connector.connect_url() Status_code = %i\n'
            % connection.status_code)
        return connection


    @staticmethod
    def normalize_headers(headers, to_lower=True):
        """ py2, py3 compatibility function,
        since only py2 returns keys as lower()
        This function maps a lower or upper case key to the original key.
        """
        if to_lower:
            return dict((x.lower(), x) for x in list(headers))
        return dict((x.upper(), x) for x in list(headers))


    def fetch_content(self, url, tpath=None):
        """Fetch the content.

        @param url: string of the content to fetch
        @param headers: dictionary, optional headers to use
        @param tpath: string, optional filepath to a timestamp file
                      to use in the headers
        @returns (success bool, content fetched , timestamp of fetched content,
                 content headers returned)
        """

        fheaders = self.headers

        if tpath:
            fheaders = self.add_timestamp(fheaders, tpath)

        connection = self.connect_url(url, fheaders)

        headers = self.normalize_headers(connection.headers)

        if 'last-modified' in headers:
            timestamp = connection.headers[headers['last-modified']]
        elif 'date' in headers:
            timestamp = connection.headers[headers['date']]
        else:
            timestamp = None

        if connection.status_code in [304]:
            self.output('info', 'Content already up to date: %s\n'
                % url)
            self.output('info', 'Last-modified: %s\n' % timestamp)
        elif connection.status_code not in [200]:
            self.output('error', 'Connector.fetch_content(); '
                'HTTP Status-Code was:\nurl: %s\n%s'
                % (url, str(connection.status_code)))
        else:
            self.output('info', 'New content downloaded for: %s\n'
                % url)
            return (True, connection.content, timestamp)
        return (False, '', '')


    def output(self, mode, msg):
        '''Generic output module which calls the mapped functions
        from the class's init.

        @param mode: string, one of ['info', 'error']
        @param msg: string
        '''
        kwargs = self.output_dict['kwargs-%s' % mode]
        func = self.output_dict[mode]
        func(msg, **kwargs)


    def get_env_proxies(self):
        '''Sets proxies from the environment'''
        self.proxies = {}
        for proxy in ['http_proxy', 'https_proxy']:
            prox = proxy.split('_')[0]
            self.proxies[prox] = os.getenv(proxy)
        return
