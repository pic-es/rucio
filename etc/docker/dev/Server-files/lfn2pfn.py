"""
lfn2pfn.py

Default LFN-to-path algorithms for MAGIC
"""
import re
import os
import pathlib
from datetime import (
    datetime,
    tzinfo,
    timedelta,
    timezone,
)

############################

def look_for_data(fileName) :
    fileName = fileName.replace('/','-')
    fileName = fileName.replace('_','-')
    
    try :
        date = re.search('\d{4}-\d{2}-\d{2}', fileName)
        date = datetime.strptime(date.group(), '%Y-%m-%d').date()
        return(str(date))
    except : 
        pass

    if not date :
        base, name = os.path.split(name_file)  

        file_name = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]', name)

        date = datetime.strptime(file_name[0], "%Y%m%d").date()
        return(str(date))
    
def look_for_run(fileName) :  

    try :
        run = re.search('\d{8}\.', fileName)
        if not run :
            run = re.search('_\d{8}', fileName)
            run = run[0].replace('_','')
        elif (type(run).__module__, type(run).__name__) == ('_sre', 'SRE_Match') : 
            run = run.group(0)
            run = run.replace('.','')
        else :
            run = run[0].replace('.','')
            
        return(str(run))
    except : 
        pass
    
    try :
        if not run :
            run = re.findall('\d{8}\_', fileName)
            run = run[0].replace('_','')
        return(str(run))
    except : 
        pass
    
def look_for_type_files(fileName) :
    patterns_1 = ['RAW', 'Calibrated', 'Calibrated', 'Star', 'SuperStar', 'Melibea']
    patterns_2 = ['M1', 'M2', 'ST']
    
    matching_1 = [s for s in patterns_1 if s in fileName]
    matching_2 = [s for s in patterns_2 if s in fileName]
    if matching_1 and matching_2 :
        matching = str(matching_1[0]) + '_' + str(matching_2[0])
        return(str(matching))

def look_for_sources(path) :
    
    base, file_name = os.path.split(path)
    run = str(look_for_run(file_name))

    file_name = re.findall(r'[A-Z]_([^"]*)-W', file_name)
    if not file_name: 
        file_name = os.path.basename(path)
        file_name = file_name.replace(pathlib.Path(file_name).suffix, '')

        file_name = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]', file_name)

        file_name = [i for i in file_name if not i.isdigit()]
        file_name = max(file_name, key=len)    
    else :
        file_name = file_name[0].replace('+','-')
        
    if run in file_name : 
        file_name = file_name.replace(run,'')
        
    return(str(file_name))

############################

def groups(name_file) :
    organization = dict();

    f_name = os.path.basename(name_file)

    organization['replica'] = f_name.replace('+','_')
    organization['dataset_1'] = look_for_run(name_file)
    organization['container_1'] = look_for_data(name_file)
    organization['container_2'] = look_for_sources(name_file)
    organization['container_3'] = look_for_type_files(name_file)  
    organization['name'] = "/".join(filter(bool, [look_for_type_files(name_file),look_for_sources(name_file),look_for_data(name_file),look_for_run(name_file)]))
    organization['fullname'] = "/".join(filter(bool, [look_for_type_files(name_file),look_for_sources(name_file),look_for_data(name_file),look_for_run(name_file),f_name.replace('+','_')]))
    return(organization)

############################


if __name__ == '__main__':

    def test_magic_mapping(lfn):
        """Demonstrate the LFN->PFN mapping"""
        mapped_pfn = groups(name)
        print(mapped_pfn)

    test_magic_mapping("testing", "root://xrootd.pic.es:1094/pnfs/pic.es/data/escape/rucio/pic_inject/Magic-test/data/M1/OSA/Calibrated/2020/02/03/20200203_M1_10284097.005_D_CrabNebula-W0.40+035.root")
    test_magic_mapping("testing", "root://xrootd.pic.es:1094/pnfs/pic.es/data/escape/rucio/pic_inject/Magic-test/data/M1/OSA/Calibrated/2020/02/03/20200203_M1_10382583.007_D_Perseus-MA-W0.26+288.root")
    test_magic_mapping("testing", "root://xrootd.pic.es:1094/pnfs/pic.es/data/escape/rucio/pic_inject/Magic-test/data/ST/OSA/SuperStar/2020/02/03/superstar75939036.root")
    test_magic_mapping("testing", "root://xrootd.pic.es:1094/pnfs/pic.es/data/escape/rucio/pic_inject/Magic-test/data/ST/OSA/Melibea/2020/02/03/melibea39615589.root")
