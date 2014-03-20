import os
import tempfile
import zipfile
import shutil
import ckan.lib.dumper as dumper
import ckan.plugins as plugins
import ckan.lib.uploader as uploader

def exportPackages(query):
    
    #create temporary directory
    tmp_dir = tempfile.mkdtemp()
                 
    #dump package to json   
    file_json = open('%s/package.json' % tmp_dir, 'w')
    dumper.SimpleDumper().dump_json(file_json, query)
    file_json.flush()
    
    #dump package to csv   
    file_csv = open('%s/package.csv' % tmp_dir, 'w')
    dumper.SimpleDumper().dump_csv(file_csv, query)
    file_csv.flush()
    
    #add resource files to tmp directory
    for pkg in query:
        pkg_dict = pkg.as_dict()
        resources = pkg_dict['resources']
        
        for resource in resources:
            if resource['url_type'] == 'upload':
                #copy file
                try:
                    upload = uploader.ResourceUpload(resource)
                    filepath = upload.get_path(resource['id'])
                    shutil.copyfile(filepath, '%s/%s_%s' % (tmp_dir,resource['id'],resource['url'].split('/')[-1]))
                except:
                    pass
            
    
    #zip directory up
    file_zip_path = '%s.zip' % tmp_dir
    file_zip = zipfile.ZipFile(file_zip_path, 'w')
    zipdir(tmp_dir, file_zip)
    file_zip.close()
    
    #remove tmp directory
    shutil.rmtree(tmp_dir)
    
    return file_zip_path

def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file), file)