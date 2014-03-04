import ckan.plugins as plugins


class DSActionsPluginClass(plugins.SingletonPlugin):
    """
    Setup plugin
    """
    print '#############################'
    print '#     ckanext-dsactions     #'
    print '#############################'


    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

    def before_map(self, map):

        map.connect('actions', '/dataset/actions/{id}',
            controller='ckanext.dsactions.controller:ActionController',
            action='index')

        map.connect('export', '/dataset/export/{id}',
            controller='ckanext.dsactions.controller:ActionController',
            action='export')


        return map

    def update_config(self, config):
        plugins.toolkit.add_template_directory(config, 'templates')
