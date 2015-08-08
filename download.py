#! /usr/bin/python
import requests 
import shutil 
import zipfile
import os

def download(dldir = ''):
    preurl_default = 'http://www.who.int/entity/healthinfo/statistics/'
    preurl_pop = 'http://www.who.int/entity/healthinfo/'
    filesuff = '.zip'
    urlparams = {'ua': 1}
    filelist = ['documentation', 'availability', 'country_codes', 'notes', 'Pop', 
            'morticd07', 'morticd08', 'morticd09', 'Morticd10_part1', 'Morticd10_part2']

    for filename in filelist:
        filefullname = filename + filesuff
        dlpath = os.path.join(dldir, filefullname)
        if filename == 'Pop':
            preurl = preurl_pop
        else:
            preurl = preurl_default
        url = preurl + filefullname
        print(url)
        print(dlpath)
        r  =  requests.get(url, params = urlparams, stream = True)
        out_file = open(dlpath, 'wb')
        shutil.copyfileobj(r.raw, out_file)
        out_file.close()
        del r
        zf = zipfile.ZipFile(dlpath, 'r')
        zf.extractall(path = dldir)
        zf.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        download(sys.argv[1])
    else:
        download()
