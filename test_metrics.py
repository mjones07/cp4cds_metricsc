# need to test the metrics

from metrics import *
from unittest import TestCase

# opendap tests
class test_opendap_download(TestCase):
    def test_fail(self):

        ret_val = download_check([])
        self.assertFalse(ret_val)

    def test_pass(self):

        ret_val = download_check([])
        self.assertTrue(ret_val)

# esgf search tests
class test_esgf_search(TestCase):
    def test_fail(self):

        esgf_search_uris = ['https://index.mips.copernicus-climate.eu/esg-search']
        esgf_search_proj_names = ['bad_name']
        var_standard_names = ['air_temperature']
        total_expected_hits = [27475]
        var_expected_hits = [3557]

        retval = esgf_search(esgf_search_uris[0],
                                 esgf_search_proj_names[0],
                                 var_standard_names[0],
                                 total_expected_hits[0],
                                 var_expected_hits[0])

        self.assertFalse(retval)

    def test_pass(self):
        esgf_search_uris = ['https://index.mips.copernicus-climate.eu/esg-search']
        esgf_search_proj_names = ['c3s-cmip5']
        var_standard_names = ['air_temperature']
        total_expected_hits = [27475]
        var_expected_hits = [3557]

        retval = esgf_search(esgf_search_uris[0],
                                 esgf_search_proj_names[0],
                                 var_standard_names[0],
                                 total_expected_hits[0],
                                 var_expected_hits[0])

        self.assertTrue(retval)
