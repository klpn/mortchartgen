#! /usr/bin/python
import os
import subprocess 

def tableimp(dldir=''):
    filelist=['MortIcd7','Morticd8','Morticd9','Morticd10_part1','Morticd10_part2','pop']

    for filename in filelist:
        dlpath=os.path.join(dldir,filename)
        if filename=='pop':
            temppath=os.path.join(dldir,'Pop')
        else:
            temppath=os.path.join(dldir,'Deaths')
        os.rename(dlpath,temppath)
        subprocess.call(['mysqlimport','--defaults-extra-file=tableimp.cnf','Morticd',temppath])
        os.rename(temppath,dlpath)

if __name__=='__main__':
    import sys
    if len(sys.argv)>1:
        tableimp(sys.argv[1])
    else:
        tableimp()
