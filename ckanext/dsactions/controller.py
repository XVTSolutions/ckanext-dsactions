import datetime
import pylons
import ckan
import ckan.lib.helpers as h
from ckan.lib.base import BaseController
import ckan.plugins as plugins

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

            if post_data['action-type'] == 'export':
                print 'export'
                #task 1: work out if the dataset has items in filestore

            if post_data['action-type'] == 'clone':

                context = {'model': ckan.model,
                   'session': ckan.model.Session,
                   'user': pylons.c.user or pylons.c.author}

                try:
                    plugins.toolkit.check_access('package_create', context)
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


                #create a new one based on existing one...
                try:
                    #for some reason, the pkg_dict given to 'package_create' still has the old id
                    pkg_dict_new = plugins.toolkit.get_action('package_create')(context, pkg_dict)
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
            return plugins.toolkit.render("dsaction-index.html", extra_vars=vars)


