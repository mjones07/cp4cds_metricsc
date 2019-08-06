#!/usr/bin/env python
"""Script to run Flask Prometheus app
"""
__author__ = "P J Kershaw"
__date__ = "13/07/19"
__copyright__ = "Copyright 2019 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
from builtins import __import__
import sys
import os
import inspect
import unittest
import logging
from argparse import ArgumentParser

from ceda.unittest_prometheus_wrapper.flask_app import flask_app_factory


log = logging.getLogger(__name__)

# There doesn't seem to be a way of getting this list through logging's public
# interface - resorting to '_' 'protected' var
LOG_LEVEL_NAMES = logging._nameToLevel.keys()
LOG_LEVEL_NAMES_STR = ', '.join(LOG_LEVEL_NAMES)
LOG_LEVEL_NAMES_OPT_STR = '|'.join(LOG_LEVEL_NAMES)

   
class PrometheusScriptConfigError(Exception):
    '''Error with configuration settings for Prometheus web application
    start up script
    '''
    
     
def main(log_level=logging.WARN, run_service=True):
    '''Run prometheus Flask app'''

    options = '[-h] [-s] [-c] [-n] [-p]'
    description = (
        'Prometheus Flask web app script to run unit tests.  Specify a '
        'unit test case class and optionally, one or more test methods to run'
        '.  If no test methods are specified, all tests from <test case class'
        '> are run and aggregate UP/DOWN result is collected.  The '
        'Prometheus endpoint is exposed as /metrics/<test case name>/'
        '<test method> or if no test methods are specified, /metrics/<test '
        'case name>/'
    )

    parser = ArgumentParser(usage='%(prog)s ' + options,
                            description=description)

    log_level_s = logging._levelToName.get(log_level)
    if log_level is None:
        raise PrometheusScriptConfigError(
            'Unrecognised default log-level set.  Use one of: {}'.format(
                LOG_LEVEL_NAMES_STR))

    parser.add_argument("-s", "--service-name",
                        dest="service_name", 
                        default=None,
                        metavar="<test case class>",
                        help="Service name to be displayed in output from "
                            "Prometheus endpoint (defaults to <test case "
                            "class> name")
    
    parser.add_argument("-c", "--test-class",
                        dest="test_class_name", 
                        metavar="<test case class>",
                        required=True,
                        help="Name of test case class to integrate into "
                            "Prometheus endpoint")
                    
    parser.add_argument("-n", "--test-name",
                        dest="test_names", 
                        nargs='*',
                        metavar="<name of test>",
                        help="List of test names from <test case class> to "
                            "run.  If none are given, all tests from the "
                            "test class will be run")
                    
    parser.add_argument("-p", "--port-num",
                        dest="port_num", 
                        metavar="<port number>",
                        type=int,
                        default=int(
                            os.getenv('CEDA_PROMETHEUS_SERVICE_PORT', 5000)),
                        help="Port number to run the web service on.  "
                            "Defaults to 5000")
    
    parsed_args, _ = parser.parse_known_args()

    test_module_name, test_class_name = parsed_args.test_class_name.rsplit(
                                                                    '.', 1)
    test_module = __import__(test_module_name, globals(), locals(), 
                             [test_class_name])
    test_class = getattr(test_module, test_class_name)
    if not isinstance(unittest.TestCase, test_class):
        parser.exit(status=1, message="Expecting unittest.TestCase instance "
                    "for <test case class> argument, got {!r}".format(
                        test_class))
                    
    if parsed_args.service_name is None:
        service_name = test_class.__name__
    else:
        service_name = parsed_args.service_name
        
    app = flask_app_factory(test_class, test_names=parsed_args.test_names,
                            service_name=service_name)

    if run_service:
        app.run('127.0.0.1', parsed_args.port_num)
    else:
        return app


if __name__ == '__main__':
    main()
    
