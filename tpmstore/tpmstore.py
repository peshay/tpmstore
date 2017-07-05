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
        name:
            description:
                - Name of the entry in TeamPasswordManager. Will search for exact match.
            required: True
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


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        ret = []
        # We need at least 4 parameters: api-url, api-user, api-password, entry name
        if len(terms) < 4:
            raise AnsibleError("At least 4 arguments required.")
        # Fill the mandatory values
        tpmurl=terms.pop(0)
        tpmuser=terms.pop(0)
        tpmpass=terms.pop(0)
        # Default is just lookup
        create = False
        new_entry = {}
        for term in terms:
            if "=" in term:
                (key, value) = term.split("=")
                # entry name is mandatory
                if key == "name":
                    # get entry
                    name = value
                    new_entry.update({'name': name})
                # if not just lookup, but also create/update an entry
                if key == "create":
                    if value == "True":
                        create = True
                    elif value == "False":
                        create = False
                    else:
                        raise AnsibleError("create can only be True or False and not: {}".format(value))
                # optional parameters for create/update of an entry
                if key == "password":
                    password = value
                    new_entry.update({'password': password})
                if key == "username":
                    username = value
                    new_entry.update({'username': username})
                if key == "access_info":
                    access_info = value
                    new_entry.update({'access_info': access_info})
                if key == "tags":
                    tags = value
                    new_entry.update({'tags': tags})
                if key == "email":
                    email = value
                    new_entry.update({'email': email})
                if key == "expiry_date":
                    expiry_date = value
                    new_entry.update({'expiry_date': expiry_date})
                if key == "notes":
                    notes = value
                    new_entry.update({'notes': notes})
                if key == "reason":
                    unlock_reason = value
                # project_id is mandatory if no entry exists and create == True
                if key == "project_id":
                    project_id = value
                    new_entry.update({'project_id': project_id})

        # format the search to get an exact result for name
        search = "name:[{}]".format(name)
        try:
            if "unlock_reason" in locals():
                tpmconn = tpm.TpmApiv4(tpmurl, username=tpmuser, password=tpmpass, unlock_reason=unlock_reason)
            else:
                tpmconn = tpm.TpmApiv4(tpmurl, username=tpmuser, password=tpmpass)
            match = tpmconn.list_passwords_search(search)
        except tpm.TpmApiv4.ConfigError as e:
            raise AnsibleError("First argument has to be a valid URL to TeamPasswordManager API: {}".format(tpmurl))
        except tpm.TPMException as e:
            raise AnsibleError(e)

        # If there are no entries and we should create
        if len(match) < 1 and create == True:
            display.display("No entry found, will create: {}".format(name))
            if "project_id" in locals():
                if "password" in locals():
                    if password == "random":
                        new_password = tpmconn.generate_password().get("password")
                        new_entry.update({'password': new_password})
                        password = new_password
                try:
                    newid = tpmconn.create_password(new_entry)
                    display.display("Created new entry with ID: {}".format(newid.get('id')))
                    ret = [password]
                except tpm.TPMException as e:
                    raise AnsibleError(e)
            else:
                raise AnsibleError("To create a complete new entry, project_id is mandatory.")
        elif len(match) < 1 and create == False:
            raise AnsibleError("Found no match for: {}".format(name))
        elif len(match) > 1:
            raise AnsibleError("Found more then one match for the entry, please be more specific: {}".format(name))
        elif create == True:
            result = tpmconn.show_password(match[0])
            display.display('Will update entry "{}" with ID "{}"'.format(result.get("name"), result.get("id")))
            if "password" in locals():
                if password == "random":
                    new_password = tpmconn.generate_password().get("password")
                    new_entry.update({'password': new_password})
                    password = new_password
            try:
                tpmconn.update_password(result.get("id"),new_entry)
                ret = [password]
            except tpm.TPMException as e:
                raise AnsibleError(e)
        else:
            result = tpmconn.show_password(match[0].get("id"))
            ret = [result.get("password")]

        return ret
