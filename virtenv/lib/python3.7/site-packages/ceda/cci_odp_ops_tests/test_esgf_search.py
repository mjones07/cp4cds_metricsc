#!/usr/bin/env python
"""Test CCI Open Data Portal CSW service
"""
from nagiosplugin import result
__author__ = "P J Kershaw"
__date__ = "07/11/17"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import os
import unittest
import os

import requests

from pyesgf.search import SearchConnection, results


class EsgfSearchTestCase(unittest.TestCase):
    '''Unit test case for testing ESA CCI Open Data Portal ESGF Search
    Service'''

    ESGF_SEARCH_URI = os.environ.get(
                            'CCI_ODP_ESGF_SEARCH_URI',
                            'http://cci-odp-index.ceda.ac.uk/esg-search')
    ESGF_SEARCH_CCI_PROJ_NAME = 'esacci'
    MIN_EXPTD_DATASETS = 102
    MIN_EXPTD_SOILMOISTURE_DATASETS = 6
    MIN_EXPTD_OCEANCOLOUR_DATASETS = 40

    @classmethod
    def _search(cls, **search_kwargs):
        conn = SearchConnection(cls.ESGF_SEARCH_URI, distrib=False)
        ctx = conn.new_context(project=cls.ESGF_SEARCH_CCI_PROJ_NAME,
                               **search_kwargs)

        results = ctx.search()
        return results

    def test01_search_all(self):
        ds_results = self.__class__._search()
        self.assertGreater(ds_results.context.hit_count, 
                           self.__class__.MIN_EXPTD_DATASETS-1,
                           msg='Expecting at least {:d} datasets returned '
                               'from search'.format(
                               self.__class__.MIN_EXPTD_DATASETS))
        
        sample_index_spacing = ds_results.context.hit_count // 5
        sample_indices = [i * sample_index_spacing for i in range(5)]
        for i in sample_indices:
            ds_result = ds_results[i]
            self.assertTrue(ds_result, 
                            msg='Expecting non-null first dataset ID')
            
            sample_index = ds_result.number_of_files // 2
            file_result = ds_result.file_context().search()[sample_index]
            self.assertTrue(file_result, 
                            msg='Expecting non-null for {} download '
                            'URL'.format(sample_index))
                
    def test02_search_soilmoisture(self):
        ds_results = self.__class__._search(cci_project="SOILMOISTURE")
        self.assertGreater(ds_results.context.hit_count,
                           self.__class__.MIN_EXPTD_SOILMOISTURE_DATASETS-1,
                           msg='Expecting at least {:d} datasets returned '
                               'from search'.format(
                               self.__class__.MIN_EXPTD_SOILMOISTURE_DATASETS))

        ds = ds_results[0]

        self.assertTrue(ds, msg='Expecting non-null first dataset ID')

        f1 = ds.file_context().search()[0]
        self.assertTrue(f1, msg='Expecting non-null first download URL')

    def test03_search_oceancolour(self):
        ds_results = self.__class__._search(cci_project="OC")
        self.assertGreater(ds_results.context.hit_count,
                           self.__class__.MIN_EXPTD_OCEANCOLOUR_DATASETS-1,
                           msg='Expecting at least {:d} datasets returned '
                               'from search'.format(
                               self.__class__.MIN_EXPTD_OCEANCOLOUR_DATASETS))

        ds = ds_results[0]

        self.assertTrue(ds, msg='Expecting non-null first dataset ID')

        f1 = ds.file_context().search()[0]
        self.assertTrue(f1, msg='Expecting non-null first download URL')
