import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import time

def batchplot():
    f=open('chartgen.yaml')
    combs=yaml.safe_load(f)
    f.close()
    

    for country,countryval in combs['countries'].items():
        start_time = time.time()
        propiter(country,countryval,combs['causes'],combs['ages'])
        print(str(country) +': '+str(time.time() - start_time)+' sekunder')

def propplot(sex,country,countryval,ptype,cause,age,icdlist):
    caalias={'all':'totalt','inf':'infektioner','tb':'tuberkulos','lfinf':'luftvägsinfektioner','stihiv':'könssjukdomar/HIV','gastrinf':'magtarminfektioner','genbact':'allmänna bakterieinfektioner','infrest':'övriga infektioner','tum':'tumörer','bc':'bröstcancer','femc':'cancer kvinnliga könsorgan','malec':'cancer manliga könsorgan','pc':'prostatacancer','lc':'lungcancer','diab':'diabetes','circ':'cirkulationsorgan','hd':'hjärtsjukdom','ihd':'ischemisk hjärtsjukdom','str':'slaganfall','circnonihd':'cirkulationsorgan utom IHD','othath':'artärsjukdom utom IHD/slaganfall','circnonath':'cirkulationsorgan icke ateroskleros','chresp':'kronisk lungsjukdom','illdef':'illa definierade orsaker','ext':'yttre orsaker'}
    agealias={'Pop1':'alla åldrar','Pop2':'spädbarn','Pop38mean':'1\u201314 (genomsnitt över åldrar)','Pop914mean':'15\u201344 (genomsnitt över åldrar)','Pop1518mean':'45\u201364 (genomsnitt över åldrar)','Pop1920mean':'65\u201374 (genomsnitt över åldrar)','Pop2122mean':'75\u201384 (genomsnitt över åldrar)','Pop222sum':'0\u201384','Pop2325sum':'85\u2013'}
    ptypealias={'rate':'Dödstal','perc':'Andel dödsfall'}
    plt.legend(framealpha=0.5)
    plt.ylim(ymin=0)
    plt.title(ptypealias[ptype]+' '+caalias[cause]+' '+countryval['alias'],y=1.02)
    plt.xlabel('År')
    plt.ticklabel_format(scilimits=(-4,0),axis='y')
    plt.ylabel(ptypealias[ptype]+' '+agealias[age])

    for index,value in icdlist.iteritems(): 
        if index==countryval['startyear'] or (index-1 in icdlist and value != icdlist.loc[index-1]):
            plt.text(index,0,value,rotation=90,va='bottom',ha='center',color='red')

    plt.savefig('site/charts/'+cause+str(country)+ptype+str(sex)+age+str(countryval['startyear'])+str(countryval['endyear'])+'.svg')
    plt.close()

def propiter(country,countryval,causes,ages):
    startyear=countryval['startyear']
    endyear=countryval['endyear']
    sexalias={0:'båda',1:'män',2:'kvinnor'}
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
                        causerate[age].plot(label=sexalias[causeval['sex']])
                    elif ageval['ptype']=='perc':
                        causeperc[age].plot(label=sexalias[causeval['sex']])
                    propplot(causeval['sex'],country,countryval,ageval['ptype'],cause,age,countrydall_fem['List'])

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
                            causerate_fem[age].plot(label=sexalias[2])
                            causerate_male[age].plot(label=sexalias[1])
                        elif ageval['ptype']=='perc':
                            causeperc_fem[age].plot(label=sexalias[2]) 
                            causeperc_male[age].plot(label=sexalias[1])    
                        propplot(causeval['sex'],country,countryval,ageval['ptype'],cause,age,countrydall_fem['List'])

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
    conn_config = {'user': 'whomuser', 'password': 'whomort', 'database': 'Morticd', 'host': 'localhost', 'unix_socket': '/run/mysqld/mysqld.sock'}
    conn = mysql.connector.connect(**conn_config)
    cur=conn.cursor()
    if qtype=='mort':
        causeexpr={'all':{'07A':'A000','08A':'A000','09B':'B00','101':'1000','10':'AAA'},
                'inf':{'07A':'A(0(0[1-9]|[1-3]|4[0-3]|71|8[7-9]|9[0-2])|110)','08A':'A(0(0[1-9]|[1-3]|4[0-4]|72|89|9[0-2])|107)','09B':'B(0[1-7]$|185|220|3([1,2][0-2]|51))','101':'10(01|7[3-5])','10':'(A[0-9]|B|G0[0,3]|J[0-2]|N1[0-2])'},
                'tb':{'07A':'A00[1-5]','08A':'A0(0[6-9]|10])','09B':'B02$','101':'100[5-6]','10':'A1[5-9]'},
                'lfinf':{'07A':'A0(8[7-9]|9[0-2])','08A':'A0(89|9[0-2])','09B':'B3[1,2][0-2]','101':'107[3-5]','10':'J[0-2]'},
                'stihiv':{'07A':'A0(0[6-9]|1[0-1])','08A':'A03[4-8]','09B':'B(06$|18[4-5])','101':'10(13|20)','10':'(A(5|6[0-4])|B2[0-4])'},
                'gastrinf':{'07A':'A(0(1[2-4,6])|104)','08A':'A0(0[1-5])','09B':'B01$','101':'100[2-4]','10':'A0'},
                'genbact':{'07A':'A(0(1[5,7-9]|2[0-7]|71)|110)','08A':'A(0(1[1-9]|2[0-1]|72)|107)','09B':'B(03$|220|351)','101':'10(0[7-9]|1[0-2]|59)','10':'(A[2-4]|G0[0,3]|N1[0-2])'},
                'infrest':{'07A':'A0(2[8-9]|3|4[0-3])','08A':'A0(2[2-9]|3[0-3,9]|4[0-4])','09B':'B(0[4,5,7])$','101':'10(1[4-9]|2[1-5])','10':'(A(6[5-9]|[7-9])|B([0-1]|2[5-9]|[3-9]))'},
                'tum':{'07A':'A0(4[4-9]|5|60)','08A':'A0(4[5-9]|5|6[0-1])','09B':'B(0[8-9]$|1[0-7]$)','101':'1026','10':'(C|D[0-4])'},
                'bc':{'07A':'A051','08A':'A054','09B':'B113','101':'1036','10':'C50'},
                'femc':{'07A':'A05[2-3]|17[5-6]','08A':'18[0-4]$','09B':'B12[0-3]|184','101':'103[7-9]','10':'C5[1-8]'},
                'malec':{'07A':'A054|17[8-9]$','08A':'A057|18[6-7]$','09B':'B12[4-5]|187$','101':'1040','10':'C6[0-3]'},
                'pc':{'07A':'A054','08A':'A057','09B':'B124','101':'1040','10':'C61'},
                'lc':{'07A':'A050','08A':'A051','09B':'B101','101':'1034','10':'C3[3-4]'},
                'diab':{'07A':'A063','08A':'A064','09B':'B181','101':'1052','10':'E1[0-4]'},
                'circ':{'07A':'A0(70|79|8[0-6])','08A':'A08[0-8]','09B':'B(2[5-9]|30)$','101':'1064','10':'(I|F01)'},
                'hd':{'07A':'A0(79|8[0-4])','08A':'A08[0-4]','09B':'B2[5-8]$','101':'106[5-8]','10':'I[0-5]'},
                'ihd':{'07A':'A081','08A':'A083','09B':'B27$','101':'1067','10':'I2[0-5]'},
                'str':{'07A':'A070','08A':'A085','09B':'B29$','101':'1069','10':'(I6|F01)'},
                'othath':{'07A':'A085','08A':'A086','09B':'B30[0-2]','101':'1070','10':'I7'},
                'circnonihd':{'07A':'A0(70|79|8[0,2-6])','08A':'A08[0-2,4-8]','09B':'B(2[5-6,8-9]|30)$','101':'10(6[5-6,8-9]|7[0-1])','10':'(I([0-1]|2[6-9]|[3-9])|F01)'},
                'circnonath':{'07A':'A0(79|8[0,2-4,6])','08A':'A08[0-2,4,7-8]','09B':'B(2[5-6,8]|30[3-9])$','101':'10(6[5-6,9]|71])','10':'I([0-1]|2[6-9]|[3-5,8-9])'},
                'chresp':{'07A':'A09[3-7]','08A':'A09[3-6]','09B':'B32[3-9]','101':'107[6,7]','10':'J[3-9]'},
                'illdef':{'07A':'A13[6,7]','08A':'A13[6,7]','09B':'B46$','101':'1094','10':'R'},
                'ext':{'07A':'A1(3[8,9]|[4,5])','08A':'A1(3[8,9]|[4,5])','09B':'B(4[7-9]|5[0-6])$','101':'1095','10':'[V-Y]'}}
        sqlqkeys={'sex':sex,'country':country,'startyear':startyear,'endyear':endyear,'ca07a':causeexpr[cause]['07A'],'ca08a':causeexpr[cause]['08A'],'ca09b':causeexpr[cause]['09B'],'ca101':causeexpr[cause]['101'],'ca10':causeexpr[cause]['10']}
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
