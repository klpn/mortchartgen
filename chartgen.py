#! /usr/bin/python
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import yaml
import time
import os 
import random 
import statsmodels.api as sm
mpl.rcParams['axes.formatter.use_locale']=True
mpl.style.use('ggplot')
f=open('chartgen.yaml')
conf=yaml.safe_load(f)
f.close()

def batchplot(ages=conf['ages'],causes=combs['causes'],
        countries=conf['countries'],sexes=combs['sexes'],
        settings=conf['settings'],types=combs['ptypes']):

    os.makedirs('mortchart-site/charts',exist_ok=True)
    if settings['savecsv']: os.makedirs('csv',exist_ok=True)

    for country in countries:
        start_time = time.time()

        startyear=countries[country]['startyear']
        endyear=countries[country]['endyear']
        countrydenom=numbdict(country,startyear,endyear)
        for cause in causes:
            if(causes[cause]['sex']==0):
                sexlist=[2,1]
            else:
                sexlist=[causes[cause]['sex']]
            if(cause=='all'): causenom=numbdict(country,startyear,endyear,'nom',cause,
                    sexlist,countrydenom)
            else: causenom=numbdict(country,startyear,endyear,'nom',cause,
                    sexlist) 
            causedict={'rate':propdict('rate',False,causenom,countrydenom)}
            if(cause!='all'):
                causedict['perc']=propdict('perc',False,causenom,countrydenom)
            if settings['savecsv']:
                for ptype,val in causedict.items():
                    for sex in sexlist: val[sex].to_csv('csv/'+cause+
                            str(country)+ptype+str(sex)+'.csv') 

            for age in ages:
                ptype=ages[age]['ptype']
                if ('skip' not in causes[cause] or age not in 
                        causes[cause]['skip']) and (cause!='all' or ptype=='rate'):
                    propplot(causedict[ptype],sexlist,age)
                    plt.savefig('mortchart-site/charts/'+cause+str(country)+
                            ptype+str(causes[cause]['sex'])+age+'.svg')
                    plt.close()
        
        print(str(country) +': '+str(time.time() - start_time)+' sekunder')

def numbdict(country,startyear,endyear,numbtype='denom',cause='all',
        sexlist=[2,1],nomsrc='',countries=conf['countries']):
    if 'ctry_extrasql' in countries[country]:
        extrasql=countries[country]['ctry_extrasql']
    else:
        extrasql=''
    if numbtype=='nom':
        if nomsrc!='': numbdict={sex:nomsrc[sex]['perc'] for sex in sexlist}
        else: numbdict={sex:build_query(sex,country,startyear,endyear,'mort',
            extrasql,cause) for sex in sexlist}
    elif numbtype=='denom':
        numbdict={sex:{'rate':build_query(sex,country,startyear,endyear,'pop',
            extrasql),'perc':build_query(sex,country,startyear,endyear,'mort',extrasql)}
            for sex in sexlist}
    
    numbdict['cause']=cause
    numbdict['startyear']=startyear
    numbdict['endyear']=endyear
    numbdict['country']=country
    numbdict['sexlist']=sexlist
    return numbdict

def propdict(ptype,from_csv=False,nomdict='',denomdict='',country='',
        startyear='',endyear='',cause='',sexlist='',countries=conf['countries']):
    if(from_csv):
        propdict={sex:pd.read_csv('csv/'+cause+str(country)+ptype+
            str(sex)+'.csv',index_col='Year') for sex in sexlist}
    else:
        sexlist=nomdict['sexlist']
        cause=nomdict['cause']
        country=nomdict['country']
        startyear=nomdict['startyear']
        endyear=nomdict['endyear']
        propdict={sex:propframe(nomdict[sex],denomdict[sex][ptype]) for sex in sexlist}

    propdict['type']=ptype
    propdict['cause']=cause
    propdict['startyear']=startyear
    propdict['endyear']=endyear
    propdict['country']=country
    return propdict

def propplot(frames,plotsexes,age,ages=conf['ages'],causes=combs['causes'],
        countries=conf['countries'],sexes=combs['sexes'],types=combs['ptypes']):
    for sex in plotsexes:
        frames[sex][age].plot(label=sexes[sex]['alias'])
        plt.plot(smoother(frames[sex],age)[:,0],smoother(frames[sex],age)[:,1],
                label=sexes[sex]['alias']+' jämnad')    
    icdlist=frames[random.randint(min(plotsexes),max(plotsexes))]['List']
    plt.xlabel('År')
    plt.legend(framealpha=0.5)
    plt.ylim(ymin=0)
    plt.title(types[frames['type']]['alias']+' '+causes[frames['cause']]['alias']
            +' '+countries[frames['country']]['alias']+' '+str(frames['startyear'])
            +'\u2013'+str(frames['endyear']),y=1.02)
    plt.ticklabel_format(scilimits=(-4,0),axis='y')
    if 'note' in ages[age]:
        agenote=' ('+ages[age]['note']+')'
    else:
        agenote=''

    plt.ylabel(types[frames['type']]['alias']+' '+ages[age]['alias']+agenote)
    for index,value in icdlist.iteritems(): 
        if (index==frames['startyear'] or (index-1 in icdlist and 
            value != icdlist.loc[index-1])) and pd.notnull(value) :
            plt.text(index,0,value,rotation=90,va='bottom',ha='center',color='red')

def smoother(frame,col):
    return sm.nonparametric.lowess(frame[col],frame.index,frac=0.4)

def propframe(popnom,popdenom):
    popnom['Pop222sum']=popnom.loc[:,'Pop2':'Pop22'].sum(1)
    popdenom['Pop222sum']=popdenom.loc[:,'Pop2':'Pop22'].sum(1)
    popnom['Pop2325sum']=popnom.loc[:,'Pop23':'Pop25'].sum(1)
    popdenom['Pop2325sum']=popdenom.loc[:,'Pop23':'Pop25'].sum(1)
    prop=popnom.loc[:,'Pop1':'Pop2325sum']/popdenom.loc[:,'Pop1':'Pop2325sum']
    prop['Pop38mean']=prop.loc[:,'Pop3':'Pop8'].mean(1)
    prop['Pop914mean']=prop.loc[:,'Pop9':'Pop14'].mean(1)
    prop['Pop1518mean']=prop.loc[:,'Pop15':'Pop18'].mean(1)
    prop['Pop1920mean']=prop.loc[:,'Pop19':'Pop20'].mean(1)
    prop['Pop2122mean']=prop.loc[:,'Pop21':'Pop22'].mean(1)
    prop['List']=popnom['List']

    return prop

def build_query(sex,country,startyear,endyear,qtype,ctry_extrasql='',cause='all'):
    conn_config = conf['settings']['conn_config'] 
    causeexpr = conf['causes'][cause]['causeexpr'] 
    conn = mysql.connector.connect(**conn_config)
    cur=conn.cursor()
    if qtype=='mort':
        sqlqkeys={'sex':sex,'country':country,'startyear':startyear,
                'endyear':endyear,'ca07a':causeexpr['07A'],'ca08a':causeexpr['08A'],
                'ca09b':causeexpr['09B'],'ca101':causeexpr['101'],'ca10':causeexpr['10']}
        selstat=('Year,List,Sum(Deaths1) AS Pop1, Sum(Deaths2) AS Pop2,' 
        'Sum(Deaths3) AS Pop3, Sum(Deaths4) AS Pop4, Sum(Deaths5) AS Pop5, Sum(Deaths6) ' 
        'AS Pop6, Sum(Deaths7) AS Pop7, Sum(Deaths8) AS Pop8, Sum(Deaths9) AS Pop9,' 
        'Sum(Deaths10) AS Pop10, Sum(Deaths11) AS Pop11, Sum(Deaths12) AS Pop12,' 
        'Sum(Deaths13) AS Pop13, Sum(Deaths14) AS Pop14, Sum(Deaths15) AS Pop15,' 
        'Sum(Deaths16) AS Pop16, Sum(Deaths17) AS Pop17, Sum(Deaths18) AS Pop18,' 
        'Sum(Deaths19) AS Pop19, Sum(Deaths20) AS Pop20, Sum(Deaths21) AS Pop21,' 
        'Sum(Deaths22) AS Pop22, Sum(Deaths23) AS Pop23, Sum(Deaths24) AS Pop24,' 
        'Sum(Deaths25) AS Pop25, Sum(Deaths26) AS Pop26')
        sqlq=('select '+selstat+' from Deaths where (case ' 
        'when List=\'07A\' then Cause REGEXP %(ca07a)s '  
        'when List=\'08A\' then Cause REGEXP %(ca08a)s '
        'when List REGEXP \'09(B|N)\' then Cause REGEXP %(ca09b)s ' 
        'when List=\'101\' then Cause REGEXP %(ca101)s ' 
        'when List REGEXP \'10(M|[3-4])\' then Cause REGEXP %(ca10)s end)' 
        'and Sex=%(sex)s and (Country=%(country)s '+ctry_extrasql+')' 
        'and Year>=%(startyear)s and Year<=%(endyear)s group by Year,List order by Year')
    elif qtype=='pop':
        sqlqkeys={'sex':sex,'country':country,'startyear':startyear,'endyear':endyear}
        selstat=('Pop1, Pop2, Pop3, Pop4, Pop5, Pop6, Pop7, Pop8, Pop9, Pop10,' 
        'Pop11, Pop12, Pop13, Pop14, Pop15, Pop16, Pop17, Pop18, Pop19, Pop20,' 
        'Pop21, Pop22, Pop23, Pop24, Pop25, Pop26, Year')
        sqlq=('select '+selstat+' from Pop where Sex=%(sex)s and' 
        '(Country=%(country)s '+ctry_extrasql+') and Year>=%(startyear)s ' 
        'and Year<=%(endyear)s order by Year')
    else:
        print('Okänd frågetyp!')

    
    df=pd.read_sql_query(sqlq,conn,params=sqlqkeys,index_col='Year')
    
    cur.close()
    conn.close()

    return df

if __name__=='__main__':
    batchplot()
