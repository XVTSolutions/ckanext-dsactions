import os
import datetime
import pylons
import ckan
import ckan.lib.helpers as h
from ckan.lib.base import BaseController
import ckan.plugins as plugins
import paste.fileapp
import ckan.lib.uploader as uploader
from cgi import FieldStorage
from ckan.logic.converters import convert_package_name_or_id_to_id as convert_to_id

from ckan.common import request, response
import tempfile
import zipfile
import shutil
from export import exportPackages

class ActionController(BaseController):

    def index(self, id):
        print 'index'
        context = {'model': ckan.model,
                   'session': ckan.model.Session,
                   'user': pylons.c.user or pylons.c.author}

        try:
            plugins.toolkit.c.pkg_dict = plugins.toolkit.get_action('package_show')(context, {'id': id})
            plugins.toolkit.c.pkg = context['package']
            plugins.toolkit.c.resources_json = h.json.dumps(plugins.toolkit.c.pkg_dict.get('resources', []))
        except plugins.toolkit.ObjectNotFound:
            plugins.toolkit.abort(404, plugins.toolkit._('Dataset not found'))
        except plugins.toolkit.NotAuthorized:
            plugins.toolkit.abort(401, plugins.toolkit._('Unauthorized to read package %s') % id)

        vars = {
                'errors': {},
                'data': {
                         'title' : '',#plugins.toolkit._('Clone of {dataset}').format(dataset=plugins.toolkit.c.pkg_dict['title'])',
                         'name': ''
                         }
                }

        if plugins.toolkit.request.method == 'POST':
            post_data = plugins.toolkit.request.POST

            if post_data['action-type'] == 'clone':

                context = {'model': ckan.model,
                   'session': ckan.model.Session,
                   'user': pylons.c.user or pylons.c.author}

                try:
                    plugins.toolkit.check_access('package_create', context)
                    plugins.toolkit.check_access('package_update', context, {'id': id})
                    del context['package']
                except plugins.toolkit.NotAuthorized:
                    plugins.toolkit.abort(401, plugins.toolkit._('Unauthorized to clone this package'))

                #get current package...
                pkg_dict = plugins.toolkit.get_action('package_show')(None, {'id': id})

                #update necessary fields
                title = ckan.plugins.toolkit.request.params.getone('title')
                name = ckan.plugins.toolkit.request.params.getone('name')

                dt = datetime.datetime.now()
                pkg_dict['title'] = title
                pkg_dict['name'] = name
                pkg_dict['metadata_created'] = dt
                pkg_dict['metadata_modified'] = dt

                del pkg_dict['id']
                del pkg_dict['revision_id']
                del pkg_dict['revision_timestamp']
                
                resources = pkg_dict['resources']
                
                for resource in resources:
                    if resource['url_type'] == 'upload':
                        #copy file
                        upload = uploader.ResourceUpload(resource)
                        filepath = upload.get_path(resource['id'])
                        cfs = FieldStorage()
                        cfs.file = open(filepath)
                        cfs.filename = resource['url'].split('/')[-1]
                        resource['upload'] = cfs
                    
                    resource['created'] = dt
                    del resource['id']
                    del resource['revision_id']
                    del resource['revision_timestamp']
                del pkg_dict['resources']
                    
                #create a new one based on existing one...
                try:
                    #for some reason, the pkg_dict given to 'package_create' still has the old id
                    pkg_dict_new = plugins.toolkit.get_action('package_create')(context, pkg_dict)
                                        
                    for resource in resources:
                        resource['package_id'] = pkg_dict_new['id']
                        plugins.toolkit.get_action('resource_create')(context, resource)
                    
                except plugins.toolkit.ValidationError as ve:
                    plugins.toolkit.c.pkg_dict = plugins.toolkit.get_action('package_show')(context, {'id': id})
                    plugins.toolkit.c.pkg = context['package']
                    plugins.toolkit.c.resources_json = h.json.dumps(plugins.toolkit.c.pkg_dict.get('resources', []))
                    
                    errorsOther = dict(ve.error_dict)
                    if 'name' in errorsOther:
                        del errorsOther['name']

                    vars = {
                        'errors': ve.error_dict,
                        'errorsOther' : errorsOther,
                        'data': {
                                 'title' : title,
                                 'name': name
                                }
                       }

                    return plugins.toolkit.render("dsaction-index.html", extra_vars = vars)

                ckan.plugins.toolkit.redirect_to(controller="package", action="edit", id=pkg_dict_new['id'])

        else:
            get_data = plugins.toolkit.request.GET
            
            if 'action-type' in get_data and get_data['action-type'] == 'export':
                print 'export'
                #task 1: work out if the dataset has items in filestore
                
                #get package
                pid = convert_to_id(id, context)
                query = ckan.model.Session.query(ckan.model.Package).filter(ckan.model.Package.id == pid)
                
                file_zip_path = exportPackages(query)
                
                #serve zip file
                fileapp = paste.fileapp.FileApp(file_zip_path)
                fileapp.content_disposition(filename='%s.zip' % id) 
                status, headers, app_iter = request.call_application(fileapp)
                response.headers.update(dict(headers))
                content_type = 'application/zip'
                response.headers['Content-Type'] = content_type
                response.status = status
                
                #remove tmp zip file - not sure if this will cause issues deleting the file before it has been fully served?
                os.remove(file_zip_path)
                
                return app_iter
            
            return plugins.toolkit.render("dsaction-index.html", extra_vars=vars)
