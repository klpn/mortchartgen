#! /usr/bin/python
from sqlalchemy import create_engine
import pandas as pd
import numexpr as ne
import matplotlib.pyplot as plt
import matplotlib as mpl
import yaml
import time
import os 
import random 
import statsmodels.api as sm
mpl.rcParams['axes.formatter.use_locale'] = True
mpl.style.use('ggplot')
f = open('chartgen.yaml')
conf = yaml.safe_load(f)
f.close()

slengine = create_engine('sqlite:///chartgen.db')
deaths = pd.read_sql_table('Deaths', slengine, index_col = 'Year')
pop = pd.read_sql_table('Pop', slengine, index_col = 'Year')

def batchplot(ages = conf['ages'], causes = conf['causes'], 
        countries = conf['countries'], sexes = conf['sexes'], 
        settings = conf['settings'], types = conf['ptypes']):

    os.makedirs('mortchart-site/charts', exist_ok = True)
    if settings['savecsv']: os.makedirs('csv', exist_ok = True)

    for country in countries:
        start_time = time.time()

        startyear = countries[country]['startyear']
        endyear = countries[country]['endyear']
        countrydenom = numbdict(country, startyear, endyear)
        if settings['savecsv']:
            for sex in [2,1]:
                countrydenom[sex]['rate'].to_csv('csv/pop' + str(country) +
                        'no' + str(sex) + '.csv')
        for cause in causes:
            if (causes[cause]['sex'] == 0):
                sexlist = [2,1]
            else:
                sexlist = [causes[cause]['sex']]
            if (cause == 'all'): 
                causenom = numbdict(country, startyear, endyear, 'nom', cause, 
                    sexlist, countrydenom)
            else: 
                causenom = numbdict(country, startyear, endyear, 'nom', cause, 
                    sexlist) 
            
            if settings['savecsv']:
                for sex in sexlist:
                    causenom[sex].to_csv('csv/' + cause + str(country) + 'no' + 
                        str(sex) + '.csv')
                
            causedict = {'rate': propdict('rate', False, causenom, countrydenom)}
            if (cause != 'all'):
                causedict['perc'] = propdict('perc', False, causenom, countrydenom)
            if settings['savecsv']:
                for ptype, val in causedict.items():
                    for sex in sexlist: 
                        val[sex].to_csv('csv/' + cause + 
                            str(country) + ptype + str(sex) + '.csv') 

            for age in ages:
                ptype = ages[age]['ptype']
                if ('skip' not in causes[cause] or age not in 
                        causes[cause]['skip']) and (cause != 'all' or ptype == 'rate'):
                    propplot(causedict[ptype], sexlist, age)
                    plt.savefig('mortchart-site/charts/' + cause + str(country) + 
                            ptype + str(causes[cause]['sex']) + age + '.svg')
                    plt.close()
        
        print(str(country)  + ': ' + str(time.time() - start_time) + ' sekunder')

def numbdict(country, startyear, endyear, numbtype = 'denom', cause = 'all', 
        sexlist = [2, 1], nomsrc = '', countries = conf['countries']):
    if numbtype == 'nom':
        if nomsrc != '': 
            numbdict={sex:nomsrc[sex]['perc'] for sex in sexlist}
        else: 
            numbdict = {sex: build_query(sex, country, startyear, endyear, 'mort', 
            cause) for sex in sexlist}
    elif numbtype == 'denom':
        numbdict = {sex:{'rate':build_query(sex, country, startyear, endyear, 'pop'), 
            'perc':build_query(sex, country, startyear, endyear, 'mort')}
            for sex in sexlist}
    
    numbdict['cause'] = cause
    numbdict['startyear'] = startyear
    numbdict['endyear'] = endyear
    numbdict['country'] = country
    numbdict['sexlist'] = sexlist
    return numbdict

def propdict(ptype, from_csv = False, nomdict = '', denomdict = '', country = '', 
        startyear = '', endyear = '', cause = '', sexlist = '', countries = conf['countries']):
    if(from_csv):
        propdict = {sex: pd.read_csv('csv/'+cause+str(country)+ptype+
            str(sex) + '.csv', index_col = 'Year') for sex in sexlist}
    else:
        sexlist = nomdict['sexlist']
        cause = nomdict['cause']
        country = nomdict['country']
        startyear = nomdict['startyear']
        endyear = nomdict['endyear']
        propdict = {sex:propframe(nomdict[sex], denomdict[sex][ptype]) for sex in sexlist}

    propdict['type'] = ptype
    propdict['cause'] = cause
    propdict['startyear'] = startyear
    propdict['endyear'] = endyear
    propdict['country'] = country
    return propdict

def propplot(frames, plotsexes, age, ages = conf['ages'], causes = conf['causes'], 
        countries = conf['countries'], sexes = conf['sexes'], types = conf['ptypes']):
    for sex in plotsexes:
        frames[sex][age].plot(label = sexes[sex]['alias'])
        plt.plot(smoother(frames[sex], age)[:, 0],  smoother(frames[sex], age)[:, 1], 
                label = sexes[sex]['alias'] + ' jämnad')    
    icdlist = frames[random.randint(min(plotsexes), max(plotsexes))]['List']
    plt.xlabel('År')
    plt.legend(framealpha = 0.5)
    plt.ylim(ymin = 0)
    plt.title(types[frames['type']]['alias']+' '+causes[frames['cause']]['alias']
            + ' ' + countries[frames['country']]['alias'] + ' ' + str(frames['startyear'])
             + '\u2013' + str(frames['endyear']), y = 1.02)
    plt.ticklabel_format(scilimits = (-4, 0),  axis = 'y')
    if 'note' in ages[age]:
        agenote = ' (' + ages[age]['note'] + ')'
    else:
        agenote = ''

    plt.ylabel(types[frames['type']]['alias'] + ' ' + ages[age]['alias'] + agenote)
    for index, value in icdlist.iteritems(): 
        if (index == frames['startyear'] or (index-1 in icdlist and 
            value != icdlist.loc[index-1])) and pd.notnull(value) :
            plt.text(index, 0, value, rotation = 90, va = 'bottom', 
                    ha = 'center', color = 'red')

def smoother(frame, col):
    return sm.nonparametric.lowess(frame[col], frame.index, frac = 0.4)

def propframe(popnom, popdenom):
    prop = popnom.loc[:,'Pop1':'Pop2325sum']/popdenom.loc[:,'Pop1':'Pop2325sum']
    prop['Pop38mean'] = prop.loc[:,'Pop3':'Pop8'].mean(1)
    prop['Pop914mean'] = prop.loc[:,'Pop9':'Pop14'].mean(1)
    prop['Pop1518mean'] = prop.loc[:,'Pop15':'Pop18'].mean(1)
    prop['Pop1920mean'] = prop.loc[:,'Pop19':'Pop20'].mean(1)
    prop['Pop2122mean'] = prop.loc[:,'Pop21':'Pop22'].mean(1)
    prop['List'] = popnom['List']

    return prop

def build_query(sex, country, startyear, endyear, qtype, cause = 'all'):
    if qtype == 'mort':
        df = deaths.query('(Sex == {sex}) & (Country == {country}) & (Year >= {startyear}) &'
                '(Year <= {endyear}) & (Cause == "{cause}")'.format(**locals()))
    elif qtype == 'pop':
        df = pop.query('(Sex == {sex}) & (Country == {country}) & (Year >= {startyear}) &'
                '(Year <= {endyear})'.format(**locals()))

    return df


if __name__ == '__main__':
    batchplot()
