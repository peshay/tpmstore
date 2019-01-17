[![Build Status](https://travis-ci.org/peshay/tpmstore.svg?branch=devel)](https://travis-ci.org/peshay/tpmstore)
[![Codecov](https://codecov.io/gh/peshay/tpmstore/branch/devel/graph/badge.svg)](https://codecov.io/gh/peshay/tpmstore/branch/devel)
[![Scrutinizer](https://scrutinizer-ci.com/g/peshay/tpmstore/badges/quality-score.png?b=devel)](https://scrutinizer-ci.com/g/peshay/tpmstore/?branch=devel)
[![Python version](https://img.shields.io/pypi/pyversions/tpmstore.svg)](https://pypi.python.org/pypi/tpmstore)
[![license](https://img.shields.io/github/license/peshay/tpmstore.svg)](https://github.com/peshay/tpmstore/blob/devel/LICENSE)
[![Beerpay](https://beerpay.io/peshay/tpmstore/badge.svg?style=beer)](https://beerpay.io/peshay/tpmstore)


# tpmstore - Returns information, creates or updates entries from TeamPasswordManager

## Synopsis
Give login information to TeamPasswordManager and it can return information from TeamPasswordManager searches or even create or update entires.

## Parameters
### General parameters
<table>
  <tbody>
    <tr>
      <th>Parameter</th>
      <th>Choices/<span style="color:blue">Defaults</span></th>
      <th>Comments</th>
    </tr>
    <tr>
      <td>tpmurl</br><span style="color:red; font-size: 6pt">required</span></td>
      <td>
      </td>
      <td>URL to TeamPasswordManager API. Should always be first parameter.</td>
    </tr>
    <tr>
      <td>tpmuser</br><span style="color:red; font-size: 6pt">required</span></td>
      <td>
      </td>
      <td>User to authenticate against TeamPasswordManager API. Should always be second parameter.</td>
    </tr>
    <tr>
      <td>tpmpass</br><span style="color:red; font-size: 6pt">required</span></td>
      <td>
      </td>
      <td>Password to authenticate against TeamPasswordManager API. Should always be third parameter.</td>
    </tr>
    <tr>
      <td>search</br><span style="color:red; font-size: 6pt">required: If 'name' is not set.</span></td>
      <td>
      </td>
      <td>Searchtstring to use for the TeamPasswordManager search.</td>
    </tr>
    <tr>
      <td>name</br><span style="color:red; font-size: 6pt">required: If 'search' is not set.</span></td>
      <td>
      </td>
      <td>Name of the entry in TeamPasswordManager. Will search for exact match.</td>
    </tr>
    <tr>
      <td>return_value</br><span style="color:red; font-size: 6pt">TeamPasswordManager field</span></td>
      <td>
          <li><span style="color:blue">password</span> <-- Default </li>
          <li>any other field that TeamPasswordManager provides</li>
      </td>
      <td>Which fields from found entries should be returned.</td>
    </tr>
    <tr>
      <td>create</br><span style="color:red; font-size: 6pt">Boolean</span></td>
      <td>
          <li><span style="color:blue">False</span> <-- Default </li>
          <li>True</li>
      </td>
      <td>If False the plugin will only query for a password.</br>
        If True it will update an existing entry or create a new entry if it does not exists in TeamPasswordManager,</br>
        in this case project_id will be required.</td>
    </tr>
    <tr>
      <td>reason</br><span style="color:red; font-size: 6pt">required: If 'create' is true.</span></td>
      <td>
      </td>
      <td>If an entry is locked, an unlock reason is mandatory.</td>
    </tr>                        
  </tbody>
</table>

## Create Parameters
### When create is set to true, following values can be set
<table>
  <tbody>
    <tr>
      <th>Parameter</th>
      <th>Choices/<span style="color:blue">Defaults</span></th>
      <th>Comments</th>
    </tr>
    <tr>
      <td>project_id</br><span style="color:red; font-size: 6pt">int</span></td>
      <td>
      </td>
      <td>If a complete new entry is created, we need to assign it to an existing project in TeamPasswordManager.</td>
    </tr>
    <tr>
      <td>password</br><span style="color:red; font-size: 6pt">string</span></td>
      <td>
      </td>
      <td>Will update or set the field "password" for the TeamPasswordManager entry.</br>
        If set to "random" a new random password will be generated, updated to TeamPasswordManager and returned.</td>
    </tr>
    <tr>
      <td>username</br><span style="color:red; font-size: 6pt">string</span></td>
      <td>
      </td>
      <td>Will update or set the field "username" for the TeamPasswordManager entry.</td>
    </tr>
    <tr>
      <td>access_info</br><span style="color:red; font-size: 6pt">string</span></td>
      <td>
      </td>
      <td>Wil update or set the field "access_info" for the TeamPasswordManager entry.</td>
    </tr>
    <tr>
      <td>tags</br><span style="color:red; font-size: 6pt">string</span></td>
      <td>
      </td>
      <td>Will update or set the field "tags" for the TeamPasswordManager entry.</td>
    </tr>
    <tr>
      <td>email</br><span style="color:red; font-size: 6pt">string</span></td>
      <td></td>
      <td>Will update or set the field "email" for the TeamPasswordManager entry.</td>
    </tr>
    <tr>
      <td>expiry_date</br><span style="color:red; font-size: 6pt">string</span></td>
      <td>
      </td>
      <td>Will update or set the field "expiry_date" for the TeamPasswordManager entry.</td>
    </tr>  
    <tr>
      <td>notes</br><span style="color:red; font-size: 6pt">string</span></td>
      <td>
      </td>
      <td>Will update or set the field "notes" for the TeamPasswordManager entry.</td>
    </tr>                            
  </tbody>
</table>

## Examples
```
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
```

## Return Values
<table>
  <tbody>
    <tr>
      <th>Key</th>
      <th>Returned</th>
      <th>Description</th>
    </tr>
    <tr>
      <td>_list</td>
      <td>lists</td>
      <td>list containing the queried or created password</td>
    </tr>   
  </tbody>
</table>     
