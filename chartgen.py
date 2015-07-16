#! /usr/bin/python
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import yaml
import time
import os 

def batchplot():
    mpl.rcParams['axes.formatter.use_locale']=True
    f=open('chartgen.yaml')
    combs=yaml.safe_load(f)
    f.close()

    os.makedirs('mortchart-site/charts',exist_ok=True)

    for country,countryval in combs['countries'].items():
        start_time = time.time()
        propiter(country,countryval,combs['causes'],combs['ages'],combs['sexes'],combs['settings']['savecsv'])
        print(str(country) +': '+str(time.time() - start_time)+' sekunder')

def propplot(country,countryval,cause,causeval,age,ageval,icdlist):
    ptype=ageval['ptype']
    ptypealias={'rate':'Dödstal','perc':'Andel dödsfall'}
    plt.legend(framealpha=0.5)
    plt.ylim(ymin=0)
    plt.title(ptypealias[ptype]+' '+causeval['alias']+' '+countryval['alias']+' '+str(countryval['startyear'])+'\u2013'+str(countryval['endyear']),y=1.02)
    plt.xlabel('År')
    plt.ticklabel_format(scilimits=(-4,0),axis='y')

    if 'note' in ageval:
        agenote=' ('+ageval['note']+')'
    else:
        agenote=''

    plt.ylabel(ptypealias[ptype]+' '+ageval['alias']+agenote)

    for index,value in icdlist.iteritems(): 
        if index==countryval['startyear'] or (index-1 in icdlist and value != icdlist.loc[index-1]):
            plt.text(index,0,value,rotation=90,va='bottom',ha='center',color='red')

    plt.savefig('mortchart-site/charts/'+cause+str(country)+ptype+str(causeval['sex'])+age+'.svg')
    plt.close()

def propiter(country,countryval,causes,ages,sexes,save_csv=True):
    startyear=countryval['startyear']
    endyear=countryval['endyear']
    femalias=sexes[2]['alias']
    malealias=sexes[1]['alias']

    if 'ctry_extrasql' in countryval:
        ctry_extrasql=countryval['ctry_extrasql']
    else:
        ctry_extrasql=''

    countrypop_fem=build_query(2,country,startyear,endyear,'pop',ctry_extrasql)
    countrypop_male=build_query(1,country,startyear,endyear,'pop',ctry_extrasql)
    countrydall_fem=build_query(2,country,startyear,endyear,'mort',ctry_extrasql,'all')
    countrydall_male=build_query(1,country,startyear,endyear,'mort',ctry_extrasql,'all')

    for cause,causeval in causes.items():
        if causeval['sex']>0:
            causenom=build_query(causeval['sex'],country,startyear,endyear,'mort',ctry_extrasql,cause)
            if causeval['sex']==2:
                causerate=propframe(causenom,countrypop_fem)
                causeperc=propframe(causenom,countrydall_fem)
            elif causeval['sex']==1:
                causerate=propframe(causenom,countrypop_male)
                causeperc=propframe(causenom,countrydall_male)
            for age,ageval in ages.items():
                if 'skip' not in causeval or age not in causeval['skip']:
                    if ageval['ptype']=='rate':
                        causerate[age].plot(label=sexes[causeval['sex']]['alias'])
                    elif ageval['ptype']=='perc':
                        causeperc[age].plot(label=sexes[causeval['sex']]['alias'])
                    propplot(country,countryval,cause,causeval,age,ageval,countrydall_fem['List'])

        elif causeval['sex']==0:
            if cause=='all':
                causenom_fem=countrydall_fem
                causenom_male=countrydall_male
            else:
                causenom_fem=build_query(2,country,startyear,endyear,'mort',ctry_extrasql,cause)
                causenom_male=build_query(1,country,startyear,endyear,'mort',ctry_extrasql,cause)
                causeperc_fem=propframe(causenom_fem,countrydall_fem)
                causeperc_male=propframe(causenom_male,countrydall_male)
            causerate_fem=propframe(causenom_fem,countrypop_fem)
            causerate_male=propframe(causenom_male,countrypop_male)
            for age,ageval in ages.items():
                if 'skip' not in causeval or age not in causeval['skip']:
                    if (ageval['ptype']=='rate') or (cause!='all'):
                        if ageval['ptype']=='rate':
                            causerate_fem[age].plot(label=femalias)
                            causerate_male[age].plot(label=malealias)
                        elif ageval['ptype']=='perc':
                            causeperc_fem[age].plot(label=femalias) 
                            causeperc_male[age].plot(label=malealias)    
                        propplot(country,countryval,cause,causeval,age,ageval,countrydall_fem['List'])

        if save_csv:
            os.makedirs('csv',exist_ok=True)
            if causeval['sex']==0:
                causerate_male.to_csv('csv/'+cause+str(country)+'rate1.csv')
                causerate_fem.to_csv('csv/'+cause+str(country)+'rate2.csv')
                if cause!='all':
                    causeperc_male.to_csv('csv/'+cause+str(country)+'perc1.csv')
                    causeperc_fem.to_csv('csv/'+cause+str(country)+'perc2.csv')

            elif causeval['sex']>0:
                causerate.to_csv('csv/'+cause+str(country)+'rate'+str(causeval['sex'])+'.csv')
                causeperc.to_csv('csv/'+cause+str(country)+'perc'+str(causeval['sex'])+'.csv')

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

    return prop

def build_query(sex,country,startyear,endyear,qtype,ctry_extrasql='',cause='all'):
    f=open('chartgen.yaml')
    combs=yaml.safe_load(f)
    f.close()
    conn_config = combs['settings']['conn_config'] 
    causeexpr = combs['causes'][cause]['causeexpr'] 
    conn = mysql.connector.connect(**conn_config)
    cur=conn.cursor()
    if qtype=='mort':
        sqlqkeys={'sex':sex,'country':country,'startyear':startyear,'endyear':endyear,'ca07a':causeexpr['07A'],'ca08a':causeexpr['08A'],'ca09b':causeexpr['09B'],'ca101':causeexpr['101'],'ca10':causeexpr['10']}
        selstat='Year,List,Sum(Deaths1) AS Pop1, Sum(Deaths2) AS Pop2, Sum(Deaths3) AS Pop3, Sum(Deaths4) AS Pop4, Sum(Deaths5) AS Pop5, Sum(Deaths6) AS Pop6, Sum(Deaths7) AS Pop7, Sum(Deaths8) AS Pop8, Sum(Deaths9) AS Pop9, Sum(Deaths10) AS Pop10, Sum(Deaths11) AS Pop11, Sum(Deaths12) AS Pop12, Sum(Deaths13) AS Pop13, Sum(Deaths14) AS Pop14, Sum(Deaths15) AS Pop15, Sum(Deaths16) AS Pop16, Sum(Deaths17) AS Pop17, Sum(Deaths18) AS Pop18, Sum(Deaths19) AS Pop19, Sum(Deaths20) AS Pop20, Sum(Deaths21) AS Pop21, Sum(Deaths22) AS Pop22, Sum(Deaths23) AS Pop23, Sum(Deaths24) AS Pop24, Sum(Deaths25) AS Pop25, Sum(Deaths26) AS Pop26'
        sqlq='select '+selstat+' from Deaths where (case when List=\'07A\' then Cause REGEXP %(ca07a)s  when List=\'08A\' then Cause REGEXP %(ca08a)s when List REGEXP \'09(B|N)\' then Cause REGEXP %(ca09b)s when List=\'101\' then Cause REGEXP %(ca101)s when List REGEXP \'10(M|[3-4])\' then Cause REGEXP %(ca10)s end) and Sex=%(sex)s and (Country=%(country)s '+ctry_extrasql+') and Year>=%(startyear)s and Year<=%(endyear)s group by Year,List order by Year'
    elif qtype=='pop':
        sqlqkeys={'sex':sex,'country':country,'startyear':startyear,'endyear':endyear}
        selstat='Pop1, Pop2, Pop3, Pop4, Pop5, Pop6, Pop7, Pop8, Pop9, Pop10, Pop11, Pop12, Pop13, Pop14, Pop15, Pop16, Pop17, Pop18, Pop19, Pop20, Pop21, Pop22, Pop23, Pop24, Pop25, Pop26, Year'
        sqlq='select '+selstat+' from Pop where Sex=%(sex)s and (Country=%(country)s '+ctry_extrasql+') and Year>=%(startyear)s and Year<=%(endyear)s order by Year'
    else:
        print('Okänd frågetyp!')

    
    df=pd.read_sql_query(sqlq,conn,params=sqlqkeys,index_col='Year')
    
    cur.close()
    conn.close()

    return df

if __name__=='__main__':
    batchplot()
