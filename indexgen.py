#! /usr/bin/python
import yaml
import re 
from jinja2 import Environment, FileSystemLoader

f=open('chartgen.yaml')
combs=yaml.safe_load(f)
f.close()

for key in combs['countries'].keys():
    combs['countries'][key]['name']=key
countries_sorted=sorted(combs['countries'].values(),key=lambda k: (k['countryclass'], k['alias']))

for key in combs['causes'].keys():
    combs['causes'][key]['name']=key
causes_sorted=sorted(combs['causes'].values(),key=lambda k: k['alias'])

for key in combs['ages'].keys():
    combs['ages'][key]['name']=key
ages_sorted=sorted(combs['ages'].values(),key=lambda k: (k['ptype'], k['agegroups']))

for i in causes_sorted:
    alias=i['alias']
    alias_first=re.split('\W+', alias)[0]
    alias_cap=alias.replace(alias_first,alias_first.capitalize(),1)
    i['alias']=alias_cap

env=Environment(loader=FileSystemLoader('sitetempl'))
indextempl=env.get_template('index.templ.html')
indextempl.stream(compyrseq=list(range(1952,2022,10)),countries=countries_sorted,causes=causes_sorted,ages=ages_sorted,causeclasses=combs['causeclasses']).dump('site/index.html')

