import matplotlib as mpl
import matplotlib.pyplot as plt
import rpy2.robjects as ro
import pandas as pd
import numpy as np
import statsmodels.api as sm
import yaml
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
pandas2ri.activate()
base = importr('base')
stats = importr('stats')
mpl.rcParams['axes.formatter.use_locale'] = True
mpl.style.use('ggplot')
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.unicode'] = True
f = open('chartgen.yaml')
conf = yaml.safe_load(f)
f.close()

def paramsplot(country, cause, sex, startyear, endyear, startage, endage,
        ageformat, ptype = 'rate', pc = 'p', mortfunc = 'gompertz', 
        alphastart = 0.14, r0start = 'exp(-18)', astart = 10, taustart = 80, 
        normrate = False, plot = 'params', causes = conf['causes'], 
        countries = conf['countries'], sexes = conf['sexes'], types = conf['ptypes']):
    
    font = {'size': 14}
    caalias = conf['causes'][cause]['alias']
    sexalias = conf['sexes'][sex]['alias']
    ctryalias = conf['countries'][country]['alias']
    paramlabs = {'log_r0': r'\mathrm{log}(r_0)', 
            'log_r0alpha': r'\mathrm{log}\frac{r0}{\alpha}', 
            'alpha': r'\alpha', 'I(a - 1)': '(a-1)', 'a': 'a', 
            'trans_atau': r'\mathrm{log}\frac{a}{\tau}-(a-1)\mathrm{log}(\tau)',
            'minalog_tau': r'-a\mathrm{log}(\tau)'}

    ro.r('source("specchartgen.r")')
    normratestr = str(normrate).upper()
    partest = ro.r('lmortfunc.test({country}, "{cause}", {sex}, {startyear}, \
            {endyear}, {startage}, {endage}, {ageformat}, type="{ptype}", \
            pc="{pc}", mortfunc="{mortfunc}", alphastart={alphastart}, \
            r0start={r0start}, astart={astart}, taustart={taustart}, \
            normrate={normratestr})'.format(**locals()))
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
    
    plotconf = {'gompertz': {'funclab': 'Gompertz', 
        'xcol': {'rate': 'alpha', 'surv': 'alpha'}, 
        'ycol': {'rate': 'log_r0', 'surv': 'log_r0alpha'}, 'i': -k},
        'weibull': {'funclab': 'Weibull', 'xcol': {'rate': 'I(a - 1)', 'surv': 'a'},
            'ycol': {'rate': 'trans_atau', 'surv': 'minalog_tau'}, 'i': np.exp(-k)},
        'ptypelab': {'rate': 'dödstal', 'surv': 'överlevnad'}}
    
    xcol = plotconf[mortfunc]['xcol'][ptype]
    ycol = plotconf[mortfunc]['ycol'][ptype]
    funclab = plotconf[mortfunc]['funclab']
    i = plotconf[mortfunc]['i']
    ptypelab = plotconf['ptypelab'][ptype]
    
    plottitle = '{funclab}analys {ptypelab} {caalias}\n \
                {sexalias} [{startage}, {endage}] \
                {ctryalias} {pcstring} {yrstring}'.format(**locals())
    plt.close()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if (plot == 'params'):
        ax.scatter(pardata[xcol], pardata[ycol])
        ax.set_xlabel('$' + paramlabs[xcol] + '$')
        ax.set_ylabel('$' + paramlabs[ycol] + '$')
        paramstring = ('$' + paramlabs[ycol] + r'\approx' + coeff_form(k) + 
            paramlabs[xcol] + '+' + coeff_form(b) + '$')
        rsqstring = r'$R^2\approx' + coeff_form(rsq) + '$'
        istring = r'$i\approx' + coeff_form(i) + '$'
        for string, ypos in [(paramstring, 0.9), (rsqstring, 0.84), (istring, 0.78)]:
            ax.text(0.98, ypos, string, transform=ax.transAxes,
                    fontdict = font, ha = 'right')
    elif (plot == 'yrs'):
        pardata[xcol].plot()
        ax.plot(sm.nonparametric.lowess(pardata[xcol], 
            pardata.index,frac=0.4)[:,1])
        ax.set_ylabel('$' + paramlabs[xcol] + '$')
        ax.set_xlabel(yrlab)
    
    ax.set_title(plottitle) 

    return {'figure': fig, 'test': partest, 'country': country, 'cause': cause, 
            'sex': sex, 'mortfunc': mortfunc, 'ptype': ptype, 'plottitle': plottitle}

def coeff_form(coeff):
    return str(round(coeff, 3)).replace('.', '{,}')

def obspred_plot(paramsplot, fityrs, startage, endage, 
        trans = 'none'):
    obsframe = paramsplot['test'].rx2('obs')
    ptype = paramsplot['ptype']
    obsage = obsframe.rx2('age')
    predage = base.seq(startage, endage, by = 5)
    xlinlab = r'$\mathrm{log}(t)$'
    ratelinlab = r'$\mathrm{log}(r(t))$'
    survlinlab = r'$\mathrm{log}[-\mathrm{log}[S(t)]]$'
    plotlabs = {'none': {'x': '$t$', 'rate': '$r(t)$', 'surv': '$S(t)$'},
            'gomp_lin': {'x': '$t$', 'rate': ratelinlab, 'surv': survlinlab},
            'weib_lin': {'x': xlinlab,'rate': ratelinlab, 'surv': survlinlab}}
    plt.close()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    for yr in fityrs:
        obs = obsframe.rx2(str(yr))
        pred = stats.predict(paramsplot['test'].rx2('sourcefit').rx2(str(yr)), 
                newdata = ro.r['list'](age = predage)) 
        obscols = transdict(np.array(obsage), np.array(obs))
        predcols = transdict(np.array(predage), np.array(pred))
        obsplot = ax.plot(obscols[trans]['x'], obscols[trans][ptype], 
                'o', label = str(yr))
        curcolor = obsplot[0].get_color()
        predplot = ax.plot(predcols[trans]['x'], predcols[trans][ptype], 
                color = curcolor)
    
    plt.legend(loc = 2, framealpha = 0.5)
    ax.set_title('Observerad vs förutsedd ' + paramsplot['plottitle'])
    
    ax.set_xlabel(plotlabs[trans]['x'])
    ax.set_ylabel(plotlabs[trans][ptype])

def transdict(x, y):
    xlin = np.log(x)
    ratelin = np.log(y)
    survlin = np.log(-np.log(y))
    return {'none': {'x': x, 'rate': y, 'surv': y},
            'gomp_lin': {'x': x, 'rate': ratelin, 'surv': survlin},
            'weib_lin': {'x': xlin, 'rate': ratelin, 'surv': survlin}}
