import matplotlib as mpl
import matplotlib.pyplot as plt
import rpy2.robjects as ro
import pandas as pd
import yaml
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
pandas2ri.activate()

mpl.rcParams['axes.formatter.use_locale'] = True
mpl.style.use('ggplot')
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.unicode'] = True
f = open('chartgen.yaml')
conf = yaml.safe_load(f)
f.close()

def paramsplot(country, cause, sex, startyear, endyear, startage, endage,
        ageformat, ptype = 'rate', pc = 'p', 
        alphastart = 0.14, r0start = 'exp(-18)', plot = 'params',
        causes = conf['causes'], countries = conf['countries'],
        sexes = conf['sexes'], types = conf['ptypes']):
    

    
    font = {'size': 14}
    caalias = conf['causes'][cause]['alias']
    sexalias = conf['sexes'][sex]['alias']
    ctryalias = conf['countries'][country]['alias']
    log_r0lab = r'\mathrm{log}(r_0)'
    base = importr('base')
    stats = importr('stats')
    ro.r('source("specchartgen.r")')
    partest = ro.r('lgomp.test({country}, "{cause}", {sex}, {startyear}, \
            {endyear}, {startage}, {endage}, {ageformat}, type="{ptype}", \
            pc="{pc}", alphastart={alphastart}, \
             r0start={r0start})'.format(**locals()))
    partest_sum = base.summary(partest[0])
    coef_vec = stats.coef(partest[0])
    b = coef_vec[0]
    k = coef_vec[1]
    rsq = partest_sum.rx2('r.squared')[0]
    yrseq = partest[3]
    model = partest[0].rx2('model')
    pardata = pandas2ri.ri2py(model)
    pardata.index = yrseq
    yrstring = str(yrseq[0]) + '\u2013' + str(yrseq[-1])

    if (pc == 'p'):
        pcstring = 'period'
        yrlab = 'År'
    elif (pc == 'c'):
        pcstring = 'kohort'
        yrlab = 'Födelseår'
    plottitle = 'Gompertzanalys {caalias}\n {sexalias} [{startage}, {endage}] \
            {ctryalias} {pcstring} {yrstring}'.format(**locals())
    plt.close()

    if (plot == 'params'):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(pardata['alpha'], pardata['log_r0'])
        ax.set_title(plottitle) 
        ax.set_xlabel(r'$\alpha$')
        ax.set_ylabel('$' + log_r0lab + '$')
        paramstring = ('$' + log_r0lab + r'\approx' + coeff_form(k) + 
            r'\alpha +' + coeff_form(b) + '$')
        rsqstring = r'$r^2\approx' + coeff_form(rsq) + '$'
        ax.text(0.5, 0.9, paramstring, transform=ax.transAxes, fontdict = font)
        ax.text(0.5, 0.84, rsqstring, transform=ax.transAxes, fontdict = font)
    elif (plot == 'yrs'):
        pardata['alpha'].plot()
        plt.ylabel(r'$\alpha$')
        plt.xlabel(yrlab)
        plt.title(plottitle)

def coeff_form(coeff):
    return str(round(coeff, 3)).replace('.', '{,}')

