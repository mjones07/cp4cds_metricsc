#!/usr/bin/env python
"""Classes to wrap unittest test cases for running programmatically
"""
__author__ = "P J Kershaw"
__date__ = "13/07/19"
__copyright__ = "Copyright 2019 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
import sys
import os
import unittest
import logging


log = logging.getLogger(__name__)


class TestCaseRunner:
    '''Run tests from a `unittest.TestCase`'''
    
    def __init__(self, unittestcase_class, test_name=None):
        '''Run the tests in a TestCase class or run a single test if
        `test_name` is given
        '''
        self._unittestcase_class = unittestcase_class
        self._test_name = test_name

    def run(self):
        '''Run test or tests from input unittest case'''

        if self._test_name is not None:
            test_suite = unittest.TestSuite()
            test_suite.addTest(self._unittestcase_class(self._test_name))
        else:
            test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(
                                                    self._unittestcase_class)
        
        result = unittest.TestResult()
        test_suite.run(result)

        n_failures = len(result.failures)
        n_errors = len(result.errors)
        n_problems = n_failures + n_errors

        # If the whole test case is run then multiple tests will be executed
        # so need to cater for multiple results:
        if n_problems > 0:
            # Log all the rest
            for error in result.errors:
                log.error(error[0])
                
            # Log all the rest
            for failure in result.failures:
                log.error(failure[0])
                
            return False
        else:
            # Overall pass
            return True

