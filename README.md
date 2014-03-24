ckanext-dsactions
===========

Adds an 'Actions' tab when you view a dataset (as a user with editing permission for the dataset). The Actions tab contains the clone feature and can easily be extended to include other things to 'action' against a dataset.

Install
------

`cd /usr/lib/ckan/default/src/`

`git clone https://github.com/XVTSolutions/ckanext-dsactions`

`python ckanext-dsactions/setup.py develop`


Add `dsactions` to your .ini file

When paster serve (or apache) runs this.

Export
------
Can export the entire db with the following command:

`paster --plugin=ckanext-dsactions export -c /etc/ckan/default/development.ini`


