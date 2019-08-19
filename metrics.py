import prometheus_client as pc
from flask import Flask, Response
import ceda.cci_odp_ops_tests.test_tds_opendap as cedaopendap
import ceda.cci_odp_ops_tests.test_esgf_search as cedaesgf
from pyesgf.search import SearchConnection, results
from pydap.client import open_url
import os

# needs to do tests and logging


def esgf_search(esgf_search_uri, esgf_search_proj_name, var_standard_name, total_exp_hits, var_exp_hits):
    conn = SearchConnection(esgf_search_uri)
    ctx = conn.new_context(project=esgf_search_proj_name,
                           )

    # project search
    results = ctx.search()
    hits = results.context.hit_count

    if hits >= total_exp_hits:
        ret_val = 1
    else:
        return 0

    # variable
    if var_standard_name is not None:
        ctx = conn.new_context(project=esgf_search_proj_name,
                               cf_standard_name=var_standard_name)
        results = ctx.search()
        hits = results.context.hit_count
        if hits >= var_exp_hits:
            ret_val = 1
        else:
            return 0

    return ret_val

def esgf_search_check():

    # all c3s-cmip5
    esgf_search_uris = ['https://index.mips.copernicus-climate.eu/esg-search']
    esgf_search_proj_names = ['c3s-cmip5']
    var_standard_names = ['air_temperature']
    total_expected_hits = [27475]
    var_expected_hits = [3557]

    for i in range(len(esgf_search_uris)):
        retval = esgf_search(esgf_search_uris[i],
                    esgf_search_proj_names[i],
                    var_standard_names[i],
                    total_expected_hits[i],
                    var_expected_hits[i])

        if retval == 0:
            return 0

    return retval



def download_check(dap_uri):
    if not dap_uri:
        return 0

    dataset = open_url(dap_uri)
    if not dataset:
        return 0
    variables = list(dataset.keys())
    var1_name = variables[0]
    var1 = dataset[var1_name]

    if not var1.dimensions:
        return 0

    return 1


def opendap_check():
    dap_uris = []# needs authenticating to download ['https://data.mips.copernicus-climate.eu/thredds/dodsC/esg_c3s-cmip5/output1/BCC/bcc-csm1-1-m/amip/day/atmos/day/r1i1p1/rsds/v20181201/rsds_day_bcc-csm1-1-m_amip_r1i1p1_19790101-19931231.nc.html']

    for dap_uri in dap_uris:
        if download_check(dap_uri):
            pass
        else:
            return 0

    return 1

class FlaskPrometheusView:
    '''Make a view for each test to be executed.  Express this view as a class
    in order to maintain state information about the test class name and
    test to be executed.
    '''

    def __init__(self, service_status_list):
        '''Initialise the test case runner from the test class and test
        name.  Also take a reference to the Prometheus Enum service status
        '''
        self.service_status_list = service_status_list


    def __call__(self):
        '''Use call method to make instances of this class a callable
        function to which a Flask view can be attached
        '''

        total_service = []

        # esgf search
        esgf_status = esgf_search_check()
        self.service_status_list['esgf_search'].set(esgf_status)
        total_service.append(esgf_status)

        # opendap test
        opendap_status = opendap_check()
        self.service_status_list['opendap'].set(opendap_status)
        total_service.append(opendap_status)

        # Node test
        node_status = 0
        self.service_status_list['node'].set(opendap_status)
        total_service.append(node_status)

        # all services running?
        if all(total_service):
            self.service_status_list['service'].set(1)
        else:
            self.service_status_list['service'].set(0)

        return Response(pc.generate_latest(),
                        mimetype='text/plain; charset=utf-8')


def flask_app_factory():#test_class, test_names=None, service_name=None):
    '''Create a Prometheus endpoint from a test class and test names to
    be executed

    taken from Phil's https://github.com/cedadev/ceda-unittest-prometheus-wrapper/blob/devel/ceda/unittest_prometheus_wrapper/flask_app.py

    metrics we need are

    - data node availability
        - do a download
    - index node availability
        - respond to query
    - compute node availability
        - available to recieve and process job

    # stretch goals

    - if ecmwf provide a way to measure performance then those metrics
    - random testing on threads/ esgf catalogue
    - runtime of compute node jobs
    - utilisations of compute node resources
    - request duration for index/data nodes
    '''

    app = Flask(__name__)


    # Create list to append metrics to
    service_status_list = {}

    # Do tests to get the overall service status

    # Index node availability
    # need to set the correct env vars

    
    # esgf search
    esgf_status_gauge = pc.Gauge('esgf_search', 'esgf search test')
    service_status_list['esgf_search'] = esgf_status_gauge

    # opendap download
    opendap_status_gauge = pc.Gauge('opendap_search', 'opendap search test')
    service_status_list['opendap'] = opendap_status_gauge

    # node test
    node_status_gauge = pc.Gauge('node_test', 'processing node test')
    service_status_list['node'] = node_status_gauge




    # overall service status
    _service_status = pc.Gauge('overall', 'up(1)/down(0) status of service')
    service_status_list['service']=_service_status

    flask_view = FlaskPrometheusView(service_status_list)

    path = '/metrics/'
    app.add_url_rule(path, 'metrics', flask_view)







    return app

if __name__ == '__main__':
    app = flask_app_factory()#test_class, test_names=parsed_args.test_names,
    #service_name=service_name)
    app.run('0.0.0.0', '8091')
