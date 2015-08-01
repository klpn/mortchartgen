#! /usr/bin/python
import yaml
import re 
import sys 
from jinja2 import Environment, FileSystemLoader

f=open('../chartgen.yaml')
conf=yaml.safe_load(f)
f.close()

for key in conf['countries'].keys():
    conf['countries'][key]['name']=key
countries_sorted=sorted(conf['countries'].values(),key=lambda k: (k['countryclass'], k['alias']))

for key in conf['causes'].keys():
    conf['causes'][key]['name']=key
causes_sorted=sorted(conf['causes'].values(),key=lambda k: k['alias'])

for key in conf['ages'].keys():
    conf['ages'][key]['name']=key
ages_sorted=sorted(conf['ages'].values(),key=lambda k: (k['ptype'], k['agegroups']))

for i in causes_sorted:
    alias=i['alias']
    alias_first=re.split('\W+', alias)[0]
    alias_cap=alias.replace(alias_first,alias_first.capitalize(),1)
    i['alias']=alias_cap

env=Environment(loader=FileSystemLoader('jinjatempl'))

indexfname='index'
docfname='mortchartdoc'

indextempl=env.get_template(indexfname+'.jinja')
doctempl=env.get_template(docfname+'.jinja')
indextempl.stream(compyrseq=list(range(1952,2022,10)),countries=countries_sorted,causes=causes_sorted,ages=ages_sorted,causeclasses=conf['causeclasses']).dump(indexfname+'.html')
doctempl.stream(compyrseq=list(range(1952,2022,10)),causes=causes_sorted,causeclasses=conf['causeclasses']).dump(docfname+'_norefhead.md')

