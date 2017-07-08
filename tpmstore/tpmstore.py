#
# tpmstore - TeamPasswordManager lookup plugin for Ansible.
# Copyright (C) 2017 Andreas Hubert
# See LICENSE.txt for licensing details
#
# File: tpmstore.py
#

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
import tpm
"""
DOCUMENTATION:
    lookup: tpmstore
    version_added: "2.4"
    short_description: returns password from TeamPasswordManager
    description:
        - Queries TeamPasswordManager API to get a password from an entry.
          Entries in TeamPasswordManager can also be created or updated.

    options:
        tpmurl:
            description:
                - URL to TeamPasswordManager API. Should always be first parameter.
            required: True
        tpmuser:
            description:
                - User to authenticate against TeamPasswordManager API. Should always be second parameter.
            required: True
        tpmpass:
            description:
                - Password to authenticate against TeamPasswordManager API. Should always be third parameter.
            required: True
        search:
            description:
                - Searchtstring to use for the TeamPasswordManager search.
            required: If 'name' is not set.
            default: 'name:[name]'
        name:
            description:
                - Name of the entry in TeamPasswordManager. Will search for exact match.
            required: If 'search' is not set.
        return_value:
            description:
                - Which fields from found entries should be returned.
            required: False
            default: password
        create:
            description:
                - If False the plugin will only query for a password.
                  If True it will update an existing entry or create a new entry if it does not exists in TeamPasswordManager,
                  in this case project_id will be required.
            possible values: True, False
            default: False
        reason:
            description:
                - If an entry is locked, an unlock reason is mandatory.
    options if create=True:
        project_id:
            description:
                - If a complete new entry is created, we need to assign it to an existing project in TeamPasswordManager.
            required: Only if create=True AND no entry by "name" already exists.
        password:
            description:
                - Will update or set the field "password" for the TeamPasswordManager entry.
                  If set to "random" a new random password will be generated, updated to TeamPasswordManager and returned.
        username:
            description:
                - Wil update or set the field "username" for the TeamPasswordManager entry.
        access_info:
            description:
                - Wil update or set the field "access_info" for the TeamPasswordManager entry.
        tags:
            description:
                - Wil update or set the field "tags" for the TeamPasswordManager entry.
        email:
            description:
                - Wil update or set the field "email" for the TeamPasswordManager entry.
        expiry_date:
            description:
                - Wil update or set the field "expiry_date" for the TeamPasswordManager entry.
        notes:
            description:
                - Wil update or set the field "notes" for the TeamPasswordManager entry.
EXAMPLES:
  vars_prompt:
    - name: "tpmuser"
      prompt: "what is your TeamPasswordManager username?"
      private: no
    - name: "tpmpass"
      prompt: "what is your TeamPasswordManager password?"
      private: yes
  vars:
     tpmurl:   "https://MyTpmHost.example.com"
     retrieve_password: "{{ lookup('tpmstore', tpmurl, tpmuser, tpmpass, 'name=An existing entry name') }}"
     retrieve_username: "{{ lookup('tpmstore', tpmurl, tpmuser, tpmpass, 'name=An existing entry name', 'return_value=username')}}"
     search_by_tags: "{{ lookup('tpmstore', tpmurl, tpmuser, tpmpass, 'search=tags:sshhost') }}"
     retrieve_locked_password: "{{ lookup('tpmstore', tpmurl, tpmuser, tpmpass, 'name=An existing and locked entry name', 'reason=For Auto Deploy by Ansible') }}"
     newrandom_password: "{{ lookup('tpmstore', tpmurl, tpmuser, tpmpass, 'name=An existing entry name', 'create=True', 'password=random') }}"
     updatemore_values: "{{ lookup('tpmstore', tpmurl, tpmuser, tpmpass, 'name=An existing entry name', 'create=True', 'password=random', 'username=root', 'access_info=ssh://root@host', 'tags=root,ssh,aws,cloud', 'notes=Created by Ansible') }}"
     completenew_entry: "{{ lookup('tpmstore', tpmurl, tpmuser, tpmpass, 'name=An existing entry name', 'create=True', 'project_id=4', 'password=random', 'username=root', 'access_info=ssh://root@host', 'tags=root,ssh,aws,cloud', 'notes=Created by Ansible') }}"


RETURN:
  _list:
    description:
      - list containing the queried or created password
    type: lists
"""

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

class TermsHost(object):
    
    def __init__(self, terms):
        # We need at least 4 parameters: api-url, api-user, api-password, entry name
        if len(terms) < 4:
            raise AnsibleError("At least 4 arguments required.")
        # Fill the mandatory values
        self.tpmurl=terms.pop(0)
        self.tpmuser=terms.pop(0)
        self.tpmpass=terms.pop(0)
        self.work_on_terms(terms)
        self.verify_values()
        self.match = self.initiate_search()
    
    def verify_values(self):
        """Verify the correctness of all the values."""
        # verify if either search or name is set
        if not hasattr(self, 'name') and not hasattr(self, 'search'):
            raise AnsibleError('Either "name" or "search" have to be set.')
            
    def work_on_terms(self, terms):
        """Collect all the terms."""
        self.create = False
        self.new_entry = {}
        for term in terms:
            if "=" in term:
                (key, value) = term.split("=")
                # entry name is mandatory
                if key == "name":
                    # get entry
                    self.name = value
                    self.new_entry.update({'name': self.name})
                if key == 'search':
                    self.search = value
                if key == 'return_value':
                    self.return_value = value
                # if not just lookup, but also create/update an entry
                if key == "create":
                    if value == "True":
                        self.create = True
                    elif value == "False":
                        self.create = False
                    else:
                        raise AnsibleError("create can only be True or False and not: {}".format(value))
                # optional parameters for create/update of an entry
                if key == "password":
                    self.password = value
                    self.new_entry.update({'password': self.password})
                if key == "username":
                    self.username = value
                    self.new_entry.update({'username': self.username})
                if key == "access_info":
                    self.access_info = value
                    self.new_entry.update({'access_info': self.access_info})
                if key == "tags":
                    self.tags = value
                    self.new_entry.update({'tags': self.tags})
                if key == "email":
                    self.email = value
                    self.new_entry.update({'email': self.email})
                if key == "expiry_date":
                    self.expiry_date = value
                    self.new_entry.update({'expiry_date': self.expiry_date})
                if key == "notes":
                    self.notes = value
                    self.new_entry.update({'notes': self.notes})
                if key == "reason":
                    self.unlock_reason = value
                # project_id is mandatory if no entry exists and create == True
                if key == "project_id":
                    self.project_id = value
                    self.new_entry.update({'project_id': self.project_id})

    def initiate_search(self):
        # format the search to get an exact result for name
        if hasattr(self, 'search'):
            search = self.search
        else:
            search = "name:[{}]".format(self.name)
        # set default return_value to 'password'
        if not hasattr(self, 'return_value'):
            self.return_value = 'password'
            
        try:
            if hasattr(self, "unlock_reason"):
                self.tpmconn = tpm.TpmApiv4(self.tpmurl, username=self.tpmuser, password=self.tpmpass, unlock_reason=self.unlock_reason)
            else:
                self.tpmconn = tpm.TpmApiv4(self.tpmurl, username=self.tpmuser, password=self.tpmpass)
            match = self.tpmconn.list_passwords_search(search)
        except tpm.TpmApiv4.ConfigError as e:
            raise AnsibleError("First argument has to be a valid URL to TeamPasswordManager API: {}".format(self.tpmurl))
        except tpm.TPMException as e:
            raise AnsibleError(e)
        return match


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        ret = []
        th = TermsHost(terms)

        # If there are no entries and we should create
        if len(th.match) < 1 and th.create == True:
            display.display("No entry found, will create: {}".format(th.name))
            if hasattr(th, "project_id"):
                if hasattr(th, "password"):
                    if th.password == "random":
                        new_password = th.tpmconn.generate_password().get("password")
                        th.new_entry.update({'password': new_password})
                        th.password = new_password
                try:
                    newid = th.tpmconn.create_password(th.new_entry)
                    display.display("Created new entry with ID: {}".format(newid.get('id')))
                    ret = [th.password]
                except tpm.TPMException as e:
                    raise AnsibleError(e)
            else:
                raise AnsibleError("To create a complete new entry, project_id is mandatory.")
        elif len(th.match) < 1 and th.create == False:
            raise AnsibleError("Found no match for: {}".format(th.name))
        elif len(th.match) > 1:
            raise AnsibleError("Found more then one match for the entry, please be more specific: {}".format(th.name))
        elif th.create == True:
            result = th.tpmconn.show_password(th.match[0])
            display.display('Will update entry "{}" with ID "{}"'.format(result.get("name"), result.get("id")))
            if hasattr(th, "password"):
                if th.password == "random":
                    new_password = th.tpmconn.generate_password().get("password")
                    th.new_entry.update({'password': new_password})
                    th.password = new_password
            try:
                th.tpmconn.update_password(result.get("id"),th.new_entry)
                ret = [th.password]
            except tpm.TPMException as e:
                raise AnsibleError(e)
        else:
            result = th.tpmconn.show_password(th.match[0].get("id"))
            ret = [result.get(th.return_value)]

        return ret
