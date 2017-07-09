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
from tpm import TPMException
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

    def test_no_name_or_search_set_exception(self):
        exception_error = 'Either "name" or "search" have to be set.'
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['https://foo.bar', 'tpmuser', 'tpmass', 'return_value=foobar'])
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

    @patch('tpm.TpmApiv4.show_password', return_value={'id': 73, 'name': 'A new Entry'})
    @patch('tpm.TpmApiv4.create_password', side_effect=TPMException("Name already exists."))
    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[])
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_exception_on_create(self, mock_init, mock_search, mock_create, mock_show):
        exception_error = "Name already exists."
        tpmurl = 'https://foo.bar'
        tpmuser = 'thatsme'
        tpmpass = 'mysecret'
        search = 'A new Entry'
        project_id = '4'
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['https://foo.bar', 'tpmuser', 'tpmass', 'name={}'.format(search), 'create=True', 'project_id={}'.format(project_id)])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    @patch('tpm.TpmApiv4.show_password', return_value={'id': 73, 'name': 'A new Entry'})
    @patch('tpm.TpmApiv4.update_password', side_effect=TPMException("Can not update because of reasons."))
    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[{'id': 42}])
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_exception_on_update(self, mock_init, mock_search, mock_create, mock_show):
        exception_error = "Can not update because of reasons."
        tpmurl = 'https://foo.bar'
        tpmuser = 'thatsme'
        tpmpass = 'mysecret'
        search = 'A new Entry'
        project_id = '4'
        with self.assertRaises(AnsibleError) as context:
            self.lookup_plugin.run(['https://foo.bar', 'tpmuser', 'tpmass', 'name={}'.format(search), 'create=True', 'project_id={}'.format(project_id)])
        log.debug("context exception: {}".format(context.exception))
        self.assertTrue(exception_error in str(context.exception))

    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[{'id': 42}])
    @patch('tpm.TpmApiv4.show_password', return_value={'id': 42, 'password': 'foobar'})
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_successful_default_result(self, tpm_init_mock, tpm_show_mock, tpm_list_mock):
        unlock_reason = 'to unlock'
        result = self.lookup_plugin.run(['https://foo.bar', 'tpmuser', 'tpmass', 'name=1result', 'reason={}'.format(unlock_reason)])
        self.assertEqual(tpm_init_mock.call_args[1].get('unlock_reason'), unlock_reason)
        self.assertEqual(result, ['foobar'])

    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[{'id': 42}])
    @patch('tpm.TpmApiv4.show_password', return_value={'id': 42, 'password': 'foobar'})
    @patch('tpm.TpmApiv4.__init__', return_value=None)        
    def test_successful_search_result(self, mock_init, mock_show, mock_search):
        search = 'username:[foobar]'
        plugin_args = ['https://foo.bar', 'tpmuser', 'tpmass', 'search={}'.format(search)]
        result = self.lookup_plugin.run(plugin_args)
        self.assertEqual(mock_search.call_args[0][0], search)

    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[{'id': 42}])
    @patch('tpm.TpmApiv4.show_password', return_value={'id': 42, 'password': 'foobar', 'username': 'bar'})
    @patch('tpm.TpmApiv4.__init__', return_value=None)        
    def test_successful_return_value_result(self, mock_init, mock_show, mock_search):
        plugin_args = ['https://foo.bar', 'tpmuser', 'tpmass', 'name=1result', 'return_value=username']
        result = self.lookup_plugin.run(plugin_args)
        self.assertEqual(result[0], 'bar')

    @patch('tpm.TpmApiv4.show_password', return_value={'id': 73, 'name': 'A new Entry'})
    @patch('tpm.TpmApiv4.create_password', return_value={'id': 73})
    @patch('tpm.TpmApiv4.generate_password', return_value={'password': 'random secret'})
    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[])
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_verify_all_values_passed_at_create(self, mock_init, mock_search, mock_generate_pass, mock_create, mock_show):
        tpmurl = 'https://foo.bar'
        tpmuser = 'thatsme'
        tpmpass = 'mysecret'
        search = 'A new Entry'
        project_id = '4'
        random_password = "random secret"
        username = 'root'
        access_info = 'ssh://root@host'
        tags = 'root,ssh,aws,cloud'
        notes = 'Created by Ansible'
        reason = 'because I can'
        email = 'me@example.com'
        expiry_date = "1983-04-25"
        result = self.lookup_plugin.run([tpmurl, tpmuser, tpmpass, 'name={}'.format(search),
                                         'create=True', 'project_id={}'.format(project_id), 'password=random',
                                         'username={}'.format(username), 'access_info={}'.format(access_info),
                                         'tags={}'.format(tags), 'notes={}'.format(notes), 'email={}'.format(email),
                                         'expiry_date={}'.format(expiry_date), 'reason={}'.format(reason)])
        self.assertEqual(mock_init.call_args[0][0], tpmurl, 'tpmurl not passed')
        self.assertEqual(mock_init.call_args[1].get('username'), tpmuser, 'tpmuser not passed')
        self.assertEqual(mock_init.call_args[1].get('password'), tpmpass, 'tpmpass not passed')
        self.assertEqual(mock_init.call_args[1].get('unlock_reason'), reason, 'unlock_reason not passed')
        self.assertEqual(mock_search.call_args[0][0], 'name:[{}]'.format(search), 'search not passed')
        self.assertEqual(mock_create.call_args[0][0].get('project_id'), project_id, 'project_id not passed')
        self.assertEqual(mock_create.call_args[0][0].get('expiry_date'), expiry_date, 'expiry_date not passed')
        self.assertEqual(mock_create.call_args[0][0].get('password'), random_password, 'random_password not passed')
        self.assertEqual(mock_create.call_args[0][0].get('username'), username, 'username passed')
        self.assertEqual(mock_create.call_args[0][0].get('access_info'), access_info, 'access_info not passed')
        self.assertEqual(mock_create.call_args[0][0].get('tags'), tags, 'tags not passed')
        self.assertEqual(mock_create.call_args[0][0].get('notes'), notes, 'notes not passed')
        self.assertEqual(mock_create.call_args[0][0].get('email'), email, 'email not passed')


    @patch('tpm.TpmApiv4.show_password', return_value={'id': 73, 'name': 'An old entry'})
    @patch('tpm.TpmApiv4.update_password', return_value={'id': 73})
    @patch('tpm.TpmApiv4.generate_password', return_value={'password': 'random secret'})
    @patch('tpm.TpmApiv4.list_passwords_search', return_value=[{'id': 73}])
    @patch('tpm.TpmApiv4.__init__', return_value=None)
    def test_verify_all_values_passed_at_update(self, mock_init, mock_search, mock_generate_pass, mock_update_pass, mock_show):
        tpmurl = 'https://foo.bar'
        tpmuser = 'thatsme'
        tpmpass = 'mysecret'
        search = 'An old entry'
        project_id = '4'
        random_password = "random secret"
        username = 'root'
        access_info = 'ssh://root@host'
        tags = 'root,ssh,aws,cloud'
        notes = 'Created by Ansible'
        reason = 'because I can'
        email = 'me@example.com'
        expiry_date = "1983-04-25"
        result = self.lookup_plugin.run([tpmurl, tpmuser, tpmpass, 'name={}'.format(search),
                                         'create=True', 'project_id={}'.format(project_id), 'password=random',
                                         'username={}'.format(username), 'access_info={}'.format(access_info),
                                         'tags={}'.format(tags), 'notes={}'.format(notes), 'email={}'.format(email),
                                         'expiry_date={}'.format(expiry_date), 'reason={}'.format(reason)])
        log.debug(mock_update_pass.call_args[0][0])
        self.assertEqual(mock_init.call_args[0][0], tpmurl)
        self.assertEqual(mock_init.call_args[1].get('username'), tpmuser)
        self.assertEqual(mock_init.call_args[1].get('password'), tpmpass)
        self.assertEqual(mock_init.call_args[1].get('unlock_reason'), reason)
        self.assertEqual(mock_search.call_args[0][0], 'name:[{}]'.format(search))
        self.assertEqual(mock_update_pass.call_args[0][0], 73)
        self.assertEqual(mock_update_pass.call_args[0][1].get('project_id'), project_id)
        self.assertEqual(mock_update_pass.call_args[0][1].get('expiry_date'), expiry_date)
        self.assertEqual(mock_update_pass.call_args[0][1].get('password'), random_password)
        self.assertEqual(mock_update_pass.call_args[0][1].get('username'), username)
        self.assertEqual(mock_update_pass.call_args[0][1].get('access_info'), access_info)
        self.assertEqual(mock_update_pass.call_args[0][1].get('tags'), tags)
        self.assertEqual(mock_update_pass.call_args[0][1].get('notes'), notes)
        self.assertEqual(mock_update_pass.call_args[0][1].get('email'), email)
