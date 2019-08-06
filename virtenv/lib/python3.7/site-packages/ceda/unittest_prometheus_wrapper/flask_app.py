"""Define Prometheus Flask application
"""
__author__ = "P J Kershaw"
__date__ = "13/07/19"
__copyright__ = "Copyright 2019 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
from enum import Enum

from flask import Flask, Response
import prometheus_client 

from ceda.unittest_prometheus_wrapper.test_runner import TestCaseRunner


class ServiceStatus(Enum):
    '''Define up/down status for service'''
    DOWN = 0
    UP = 1
        
    @classmethod  
    def names(cls):
        '''Get a list of the service statuses'''
        return [i.name for i in ServiceStatus]
  

class FlaskPrometheusView:
    '''Make a view for each test to be executed.  Express this view as a class
    in order to maintain state information about the test class name and
    test to be executed.
    '''
    
    def __init__(self, service_status, test_class, test_name=None):
        '''Initialise the test case runner from the test class and test
        name.  Also take a reference to the Prometheus Enum service status
        '''
        self._test_case = TestCaseRunner(test_class, test_name=test_name)
        self._service_status = service_status
              
    def __call__(self):
        '''Use call method to make instances of this class a callable 
        function to which a Flask view can be attached
        '''
        status = self._test_case.run()
        
        # Test runner returns boolean for success/fail.  Convert this into
        # up/down enum status for Prometheus output
        self._service_status.state(ServiceStatus.names()[int(status)])
            
        return Response(prometheus_client.generate_latest(), 
                        mimetype='text/plain; charset=utf-8')


def flask_app_factory(test_class, test_names=None, service_name=None):
    '''Create a Prometheus endpoint from a test class and test names to
    be executed
    '''
    app = Flask(__name__)

    if test_names is None:
        test_names = []
        
    if service_name is None:
        service_name = '{}_status'.format(test_class.__name__)
        
    _service_status_enum = prometheus_client.Enum(service_name, 
                                               'up/down status of service', 
                                               states=ServiceStatus.names())        

    # For each test create a view
    for test_name in test_names:
        flask_view = FlaskPrometheusView(_service_status_enum, test_class, 
                                         test_name=test_name)
        
        # Path is made up of the test case class name and name of test 
        # method to be executed.
        path = '/metrics/{}/{}'.format(test_class.__name__, test_name)
        app.add_url_rule(path, test_name, flask_view)
    else:
        # No test names set - instead run all the tests in the input test case
        flask_view = FlaskPrometheusView(_service_status_enum, test_class)
        
        # Path is made up of the test case class name and name of test 
        # method to be executed.
        path = '/metrics/{}'.format(test_class.__name__)
        app.add_url_rule(path, test_class.__name__, flask_view)        
        
    return app
