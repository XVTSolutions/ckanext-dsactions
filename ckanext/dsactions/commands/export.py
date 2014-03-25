from ckan.lib.cli import CkanCommand
import ckan
import sys
import shutil
from ckanext.dsactions.export import exportPackages

class ExportCommand(CkanCommand):
    '''
    Exports all the datasets to a zip file
    
    export FILE_PATH - dumps the datsets to the given zip file
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 9
    min_args = 0

    def __init__(self,name):
        super(ExportCommand,self).__init__(name)


    def command(self):
        self._load_config()
        
        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(1)
        
        query = ckan.model.Session.query(ckan.model.Package)
        file_zip_path = exportPackages(query)
        print file_zip_path
        shutil.move(file_zip_path, self.args[0])
        print 'done'
        
        
