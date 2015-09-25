#! /usr/bin/python
from sqlalchemy import create_engine
import pandas as pd
import yaml
import time

f = open('chartgen.yaml')
conf = yaml.safe_load(f)
f.close()

conn_config = conf['settings']['conn_config']

user = conn_config['user']
password = conn_config['password']
host = conn_config['host']
database = conn_config['database']
socket = conn_config['unix_socket']

causes = conf['causes']
countries = conf['countries']
causeframes = list()

myuri = 'mysql+mysqlconnector://{user}:{password}@{host}/{database}?'\
        'unix_socket={socket}'.format(**locals())
myengine = create_engine(myuri)
sqlq = ('select Sex,Year,Country,Admin1,Pop1, Pop2, Pop3, Pop4, Pop5,' 
        'Pop6, Pop7, Pop8, Pop9, Pop10,Pop11, Pop12, Pop13, Pop14, Pop15,' 
        'Pop16, Pop17, Pop18, Pop19, Pop20, Pop21, Pop22, Pop23, Pop24,' 
        'Pop25, Pop26 from Pop')
popmod = pd.read_sql_query(sqlq, myengine)

for cause in causes:
    start_time = time.time()
    causeexpr = causes[cause]['causeexpr']
    sqlqkeys = {'ca07a': causeexpr['07A'], 'ca08a': causeexpr['08A'], 
                'ca09b': causeexpr['09B'], 'ca101': causeexpr['101'], 'ca10': causeexpr['10']}
    selstat = ('Sex,Year,List,Country,Admin1,Sum(Deaths1) AS Pop1, Sum(Deaths2) AS Pop2,' 
        'Sum(Deaths3) AS Pop3, Sum(Deaths4) AS Pop4, Sum(Deaths5) AS Pop5, Sum(Deaths6) ' 
        'AS Pop6, Sum(Deaths7) AS Pop7, Sum(Deaths8) AS Pop8, Sum(Deaths9) AS Pop9,' 
        'Sum(Deaths10) AS Pop10, Sum(Deaths11) AS Pop11, Sum(Deaths12) AS Pop12,' 
        'Sum(Deaths13) AS Pop13, Sum(Deaths14) AS Pop14, Sum(Deaths15) AS Pop15,' 
        'Sum(Deaths16) AS Pop16, Sum(Deaths17) AS Pop17, Sum(Deaths18) AS Pop18,' 
        'Sum(Deaths19) AS Pop19, Sum(Deaths20) AS Pop20, Sum(Deaths21) AS Pop21,' 
        'Sum(Deaths22) AS Pop22, Sum(Deaths23) AS Pop23, Sum(Deaths24) AS Pop24,' 
        'Sum(Deaths25) AS Pop25, Sum(Deaths26) AS Pop26')
    sqlq = ('select ' + selstat + ' from Deaths where (case ' 
        'when List=\'07A\' then Cause REGEXP %(ca07a)s '  
        'when List=\'08A\' then Cause REGEXP %(ca08a)s '
        'when List REGEXP \'09(B|N)\' then Cause REGEXP %(ca09b)s ' 
        'when List=\'101\' then Cause REGEXP %(ca101)s ' 
        'when List REGEXP \'10(M|[3-4])\' then Cause REGEXP %(ca10)s end)'
        'group by Sex,Year,List,Country,Admin1 order by Year')

    causeframe = pd.read_sql_query(sqlq, myengine, params = sqlqkeys)
    causeframe.insert(0, 'Cause', cause)
    causeframes.append(causeframe)

    print(cause  + ': ' + str(time.time() - start_time) + ' sekunder')

deathscond = pd.concat(causeframes)

framedict = {'Deaths': deathscond, 'Pop': popmod}

slengine = create_engine('sqlite:///chartgen.db')
for name, frame in framedict.items():
    frame.loc[(frame.Country == 4100) & (frame.Year < 1990), 'Country'] = 4085
    frame.loc[(frame.Country == 3150) & (frame.Year > 1974) & (frame.Admin1 != ''), 
            'Country'] = 0 
    frame_trim = frame.loc[frame.Country.isin(countries.keys()), :].copy()
    for start, end in [('3', '6'), ('2', '22'), ('23', '25')]:
        frame_trim.loc[:, 'Pop' + start + end + 'sum'] = \
            frame_trim.loc[:, 'Pop' + start: 'Pop' + end].sum(1)
    frame_trim.to_sql(name, slengine, if_exists = 'replace')
