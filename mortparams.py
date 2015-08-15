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
        ageformat, ptype = 'rate', causes = conf['causes'], countries = conf['countries'], 
        sexes = conf['sexes'], types = conf['ptypes']):
    font = {'size': 14}
    caalias = conf['causes'][cause]['alias']
    sexalias = conf['sexes'][sex]['alias']
    ctryalias = conf['countries'][country]['alias']
    log_r0lab = r'\mathrm{log}(r_0)'
    base = importr('base')
    ro.r('source("specchartgen.r")')
    partest = ro.r('lgomp.test({country}, "{cause}", {sex}, {startyear}, \
            {endyear}, {startage}, {endage}, {ageformat}, "{ptype}")'
            .format(**locals()))
    partest_sum = base.summary(partest)
    b = partest.rx2('coefficients')[0]
    k = partest.rx2('coefficients')[1]
    rsq = partest_sum.rx2('r.squared')[0]
    pardata = pandas2ri.ri2py(partest.rx2('model'))
    plt.close()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(pardata['alpha'], pardata['log_r0'])
    ax.set_title('Gompertzparametrar {caalias} {sexalias} [{startage}, {endage}] \
            {ctryalias} {startyear}\u2013{endyear}'.format(**locals())) 
    ax.set_xlabel(r'$\alpha$')
    ax.set_ylabel('$' + log_r0lab + '$')
    paramstring = ('$' + log_r0lab + r'\approx' + coeff_form(k) + 
            r'\alpha +' + coeff_form(b) + '$')
    rsqstring = r'$r^2\approx' + coeff_form(rsq) + '$'
    ax.text(0.5, 0.9, paramstring, transform=ax.transAxes, fontdict = font)
    ax.text(0.5, 0.84, rsqstring, transform=ax.transAxes, fontdict = font)

def coeff_form(coeff):
    return str(round(coeff, 3)).replace('.', '{,}')

