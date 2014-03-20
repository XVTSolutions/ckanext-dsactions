from ckan.lib.cli import CkanCommand
import ckan
from ckanext.dsactions.export import exportPackages

class ExportCommand(CkanCommand):
    '''
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 9
    min_args = 0

    def __init__(self,name):
        super(ExportCommand,self).__init__(name)


    def command(self):
        self._load_config()
        
        query = ckan.model.Session.query(ckan.model.Package)
        file_zip_path = exportPackages(query)
        print file_zip_path
        
        
        
