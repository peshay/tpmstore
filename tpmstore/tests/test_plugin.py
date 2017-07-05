# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from argparse import ArgumentParser

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import patch

from ansible.errors import AnsibleError
from ansible.module_utils import six
from tpmstore.tpmstore import LookupModule
from tpm import TpmApiv4
from logging import getLogger


log = getLogger(__name__)


class TestTpmstorePlugin(unittest.TestCase):

    def setUp(self):
        self.lookup_plugin = LookupModule()

    def test_least_arguments_exception(self):
        exception_error = 'At least 4 arguments required.'
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['tpmurl', 'tpmuser'])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    def test_create_argument_exception(self):
        wrong_term = 'Foo'
        exception_error = "create can only be True or False and not: {}".format(wrong_term)
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['tpmurl', 'tpmuser', 'tpmass', 'create={}'.format(wrong_term)])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    def test_invalid_url_exception(self):
        wrong_url = 'ftp://foo.bar'
        exception_error = "First argument has to be a valid URL to TeamPasswordManager API: {}".format(wrong_url)
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['{}'.format(wrong_url), 'tpmuser', 'tpmass', 'name=dostuff'])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    def test_other_tpm_exception(self):
        wrong_url = 'https://does.not.exists.com'
        exception_error = "Connection error for "
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['{}'.format(wrong_url), 'tpmuser', 'tpmass', 'name=dostuff'])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[{'id': 42}, {'id': 73}])
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_too_many_results_exception(self, tpm_init_mock, tpm_list_mock):
        search_sring = "2result"
        exception_error = 'Found more then one match for the entry, please be more specific: {}'.format(search_sring)
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['https://foo.bar', 'tpmuser', 'tpmass', 'name={}'.format(search_sring)])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[])
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_create_needs_projectid_exception(self, tpm_init_mock, tpm_list_mock):
        search_sring = "noresult"
        exception_error = 'To create a complete new entry, project_id is mandatory.'
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['https://foo.bar', 'tpmuser', 'tpmass', 'name={}'.format(search_sring), 'create=True'])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[])
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_no_match_found_exception(self, tpm_init_mock, tpm_list_mock):
        search_sring = "noresult"
        exception_error = "Found no match for: {}".format(search_sring)
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['https://foo.bar', 'tpmuser', 'tpmass', 'name={}'.format(search_sring), 'create=False'])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[{'id': 42}])
    @patch('tpm.TpmApiv4.show_password', return_value={'id': 42, 'password': 'foobar'})
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_successful_result(self, tpm_init_mock, tpm_show_mock, tpm_list_mock):
        unlock_reason = 'to unlock'
        result = self.lookup_plugin.run(['https://foo.bar', 'tpmuser', 'tpmass', 'name=1result', 'reason={}'.format(unlock_reason)])
        self.assertEqual(tpm_init_mock.call_args[1].get('unlock_reason'), unlock_reason)
        self.assertEqual(result, ['foobar'])
