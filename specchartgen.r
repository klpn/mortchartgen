library(ggplot2)
library(tidyr)
library(plyr)
library(yaml)
library(XML)
library(gridSVG)
library(rjson)
library(minpack.lm)
conf <- yaml.load_file('chartgen.yaml')
infs <- '\u221e'
agralias <- 'Åldersgrupp'
percalias <- '%'

comma.lab <- function(x){format(x, decimal.mark = ',')}

sexratio.trends.plot <- function(country, cause, sex1, sex2, startyear, endyear, startage, 
			       endage, type, ageformat)
{
	sex1alias <- conf[['sexes']][[sprintf('%d', sex1)]][['alias']]
	sex2alias <- conf[['sexes']][[sprintf('%d', sex2)]][['alias']]
	sex1 <- agetrends.plot(country, cause, sex1, startyear, endyear, 
			       startage, endage, type, ageformat)
	sex2 <- agetrends.plot(country, cause, sex2, startyear, endyear, 
			       startage, endage, type, ageformat)
	title <- gsub(sex1alias, sprintf('%s/%s', sex1alias, sex2alias), sex1$labels$title)
	df <- sex1$data
	df$ratio <- sex1$data$mort/sex2$data$mort
	df.plot <- ggplot(data = df, aes(x = Year, y = ratio, group = agealias, 
					 colour = agealias)) + 
		xlab('År') + ylab('Kvot') + 
		ggtitle(title) + geom_point() + geom_smooth() + 
		scale_colour_discrete(name = agralias) +
		scale_y_continuous(label = comma.lab) +	
		theme(axis.text.x = element_text(angle = 45))
	return(df.plot)
}


agetrends.plot <- function(country, cause, sex, startyear, endyear, 
			   startage, endage, type, ageformat, apctype = 'pa')
{
	csvname <- sprintf('csv/%s%d%s%d.csv', cause, country, type, sex)
	df <- read.csv(csvname, header = TRUE)
	caalias <- conf[['causes']][[cause]][['alias']]
	ctryalias <- conf[['countries']][[sprintf('%d', country)]][['alias']]
	sexalias <- conf[['sexes']][[sprintf('%d', sex)]][['alias']]
	if (ageformat == 0)
	{
		oneseq <- seq(0, 4)
		fiveseqs <- seq(5, 95, by = 5)
		fiveseqe <- seq(9, 94, by = 5)
		age <- c(oneseq, fiveseqs)
		agealias <- c(oneseq, sprintf('%d\u2013%s', fiveseqs, c(fiveseqe, infs)))
		ageorig <- sprintf('Pop%s', seq(2, 25))
	}
	else if (ageformat == 1) 
	{
		oneseq <- seq(0, 4)
		fiveseqs <- seq(5, 85, by = 5)
		fiveseqe <- seq(9, 84, by = 5)
		age <- c(oneseq, fiveseq)
		agealias <- c(oneseq, sprintf('%d\u2013%s', fiveseqs, c(fiveseqe, infs)))
		ageorig <- sprintf('Pop%s', c(seq(2, 22), '2325sum'))
	}
	else if (ageformat == 2)
	{	
		fiveseqs <- seq(5, 85, by = 5)
		fiveseqe <- seq(9, 84, by = 5)
		age <- c(0, 1, fiveseqs)
		agealias <- c(0, sprintf('%d\u2013%s', c(1, fiveseqs), c(4, fiveseqe, infs)))
		ageorig <- sprintf('Pop%s', c(2, '36sum', seq(7, 22), '2325sum'))
	}
	ages <- data.frame(age, agealias, ageorig)

	if (type == 'rate')
	{
	       	typealias <- 'Dödstal'
		yl <- 'log(dödstal)'
		yfunc <- quote(log(mort))
	}
	else if (type == 'perc')
	{       
		typealias <- 'Andel dödsfall'
	       	yl <- percalias 
		yfunc <- quote(100*mort)
	}
	title <- sprintf('%s %s %s %s', typealias, caalias, sexalias, ctryalias)


	if (ageformat == 0) 
		df.long <- gather(df, ageorig, mort, Pop2:Pop25)
	else if (ageformat == 1) 
		df.long <- gather(subset(df, 
			select = c(Year, Pop2:Pop22, Pop2325sum)), 
			ageorig, mort, Pop2:Pop2325sum)
	else if (ageformat == 2) 
		df.long <- gather(subset(df, 
			select = c(Year, Pop2, Pop36sum, Pop7:Pop22, Pop2325sum)), 
			ageorig, mort, Pop2:Pop2325sum)
	df.long <- merge(df.long, ages, 'ageorig')
	df.long.sub <- subset(df.long, Year >= startyear & Year <= endyear & 
			      age >= startage & age <= endage)
	df.long.sub$agealias <- factor(df.long.sub$agealias, 
				       levels = unique(df.long.sub$agealias[order(df.long.sub$age)]))
	df.long.sub$cohort <- df.long.sub$Year - df.long.sub$age
	yrlab <- 'År'
	cohlab <- 'Kohort'
	yrq <- quote(Year)
	cq <- quote(cohort)
	agrq <- quote(agealias)
	agq <- quote(age)
	agrscale <- quote(scale_colour_discrete(name = agralias))
	yrscale <- quote(scale_colour_gradient(name = yrlab))
	cohscale <- quote(scale_colour_gradient(name = cohlab))
	ycont <- quote(scale_y_continuous(label = comma.lab))
	
	if (apctype == 'pa')
	{
		xfunc <- yrq 
		xl <- yrlab
	       	grouper <- agrq
		scalefunc <- agrscale 
		plotsmooth <- TRUE
	        plotfunc <- quote(geom_point())
		yscfunc <- ycont
	}
	else if (apctype == 'ca')
	{
		xfunc <- cq 
		xl <- cohlab
	       	grouper <- agrq 
		scalefunc <- agrscale 
		plotsmooth <- TRUE
	        plotfunc <- quote(geom_point())	
		yscfunc <- ycont
	}
	else if (apctype == 'ap')
	{
		xfunc <- agrq 
		xl <- agralias 
	       	grouper <- yrq 
		scalefunc <- yrscale 
		plotsmooth <- FALSE
	        plotfunc <- quote(geom_line())	
		yscfunc <- ycont
	}
	else if (apctype == 'ac')
	{
		xfunc <- agrq 
		xl <- agralias
	       	grouper <- cq 
		scalefunc <- cohscale 
		plotsmooth <- FALSE
	        plotfunc <- quote(geom_line())	
		yscfunc <- ycont
	}

	env <- environment()

	df.plot <- ggplot(data = df.long.sub, aes(x = eval(xfunc), y = eval(yfunc), 
	           group = eval(grouper), colour = eval(grouper)), 
			  environment = env) + 
		xlab(xl) + ylab(yl) +  
		ggtitle(title) + 
		eval(yscfunc) + 
		eval(plotfunc) + 
		eval(scalefunc) + 
		theme(axis.text.x = element_text(angle = 45))

	if (plotsmooth)
		df.plot <- df.plot + geom_smooth()

	return(df.plot)
}

ctriesyr.batchplot <- function(compyrseq = seq(1952, 2012, by = 10))
{
	causenames <- names(conf[['causes']])
	agenames <- names(conf[['ages']])
	svgdir <- 'mortchart-site/charts/ctriesyr'
	xmlprefix <- '<?xml version = "1.0" encoding = "UTF-8"?>\n'
	dir.create(svgdir, showWarnings = FALSE)
	
	for (year in compyrseq)
	{
		for (cause in causenames)
		{
			causeconf <- conf[['causes']][[cause]]
			if (!(year %in% causeconf[['skipyrs']])){
			for (age in agenames)
			{
				
				if (!(age %in% causeconf[['skip']]))
				   {
					   type <- conf[['ages']][[age]][['ptype']]
					   if (!(cause == 'all' & type == 'perc')){
					   svgpath <- sprintf('%s/%s%s%scomp%d.svg', 
							      svgdir, cause, type, age, year)
					   curgrid <- ctriesyr.plot(cause, year, age, type)
					   print(curgrid)
					   if (causeconf[['sex']] == 0)
					   {
					   curgrid.svg <- grid.export(addClasses = TRUE)
					   cat(xmlprefix, gsub('</svg>$', '', 
							       saveXML(curgrid.svg$svg)), 
					       svgscript(curgrid$data), file = svgpath)
					   }
					   else grid.export(svgpath)
					   dev.off()

					   }
				   }
			}}
		}
	}

}

svgscript <- function(graphdata)
{
	notice <- '<!-- Adapted from http://timelyportfolio.github.io/gridSVG_intro/ -->'
	d3.script <- '<script xlink:href = "http://d3js.org/d3.v3.js"></script>'
	jsonarr <- rjson::toJSON(apply(graphdata, MARGIN = 1, FUN = function(x)return(list(x))))
	dataarr.script <- sprintf('var dataarr = %s;', jsonarr)
	datamap.script <- 'var dataToBind  =  d3.entries(dataarr.map(function(d, i) {return d[0]}));'
	databind.script <- 'var scatterPoints  =  d3.select(".points").selectAll("use");\nscatterPoints.data(dataToBind);'
	tool.script <- 'scatterPoints  
    .on("mouseover",  function(d) {      
      //Create the tooltip label
      var tooltip  =  d3.select(this.parentNode).append("g");
      tooltip
        .attr("id", "tooltip")
       tooltip.append("text")
        .attr("transform", "scale(1, -1)")
        .attr("x", 100)
        .attr("y", -590)
        .attr("text-anchor", "start")
        .attr("stroke", "gray")
        .attr("fill", "gray")      
        .attr("fill-opacity", 1)
        .attr("opacity", 1)
        .text(d.value.countryalias  +  ":");       
      tooltip.append("text")
        .attr("transform", "scale(1, -1)")
        .attr("x", 100)
        .attr("y", -570)
        .attr("text-anchor", "start")
        .attr("stroke", "gray")
        .attr("fill", "gray")
        .attr("fill-opacity", 1)
        .attr("opacity", 1)
        .text("kv: "  +  d.value.femmort.replace(".", ","));
      tooltip.append("text")
        .attr("transform", "scale(1, -1)")
        .attr("x", 100)
        .attr("y", -550)
        .attr("text-anchor", "start")
        .attr("stroke", "gray")
        .attr("fill", "gray")      
        .attr("fill-opacity", 1)
        .attr("opacity", 1)
        .text("m: "  +  d.value.malemort.replace(".", ","));
    })              
    .on("mouseout",  function(d) {       
        d3.select("#tooltip").remove();  
    });'
   return(sprintf('%s\n%s\n<script>\n%s\n%s\n%s\n%s\n</script>\n</svg>', notice, 
		  d3.script, dataarr.script, datamap.script, databind.script, tool.script))

}

ctriesyr.plot <- function(cause, compyear, ageorig, type)
{
	ctrynames <- names(conf[['countries']])
	sex <- as.numeric(conf[['causes']][[cause]][['sex']])
	caalias <- conf[['causes']][[cause]][['alias']]
	agealias <- conf[['ages']][[ageorig]][['alias']]
	if ('note' %in% names(conf[['ages']][[ageorig]])) 
		agealias <- sprintf('%s (%s)', agealias, conf[['ages']][[ageorig]][['note']])

	typealias <- conf[['ptypes']][[type]][['alias']]
	sexalias <- conf[['sexes']][[sprintf('%d', sex)]][['alias']]
	
	df <- data.frame()
	for (country in ctrynames)
	{
		if (sex == 0)
		{
			csvname.country.male <- sprintf('csv/%s%s%s1.csv', cause, country, type)
			csvname.country.fem <- sprintf('csv/%s%s%s2.csv', cause, country, type)
			df.country.male <- read.csv(csvname.country.male, header = TRUE)
			df.country.fem <- read.csv(csvname.country.fem, header = TRUE)
			df.country <- data.frame(Year = df.country.male$Year)
			df.country['malemort'] <- df.country.male[ageorig]
			df.country['femmort'] <- df.country.fem[ageorig]
		}
		else
		{
			csvname.country <- sprintf('csv/%s%s%s%d.csv', cause, country, type, sex)
			df.country.0 <- read.csv(csvname.country, header = TRUE)
			df.country <- data.frame(Year = df.country.0$Year)
			df.country['mort'] <- df.country.0[ageorig]
		}
		df.country$country <- country
		df.country$countryalias <- conf[['countries']][[country]][['alias']]
		df.country$countryiso <- conf[['countries']][[country]][['iso3166']]
		df <- rbind(df, df.country)
	}
	df.sub <- subset(df, Year == compyear)
	rownames(df.sub) <- NULL

	if (sex == 0)
	{
		title <- sprintf('%s %s\n%s %d', typealias, caalias, agealias, compyear)
		df.plot <- ggplot(data = df.sub, aes(x = femmort, y = malemort)) + 
			xlab(sprintf('%s kvinnor', typealias)) + 
			ylab(sprintf('%s män', typealias)) + 
				scale_x_continuous(label = comma.lab) + 
			scale_y_continuous(label = comma.lab) + 
			ggtitle(title) + 
			geom_text(aes(label = countryiso), size = 3.5, alpha = 1/2) + 
			geom_point(alpha = 1/8, size = 4)
	}
	else
	{
		title <- sprintf('%s %s\n%s %s %d', typealias, caalias, sexalias, 
				 agealias, compyear)
		df.plot <- ggplot(data = df.sub, aes(x = countryalias, y = mort)) + 
			xlab('Befolkning') + 
			ylab(typealias) + 
			scale_y_continuous(label = comma.lab) + 
			ggtitle(title) + 
			geom_bar(stat = 'identity') + 
			theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5))
	}
	
	return(df.plot)
	
}

causedist.plot <- function(country, sex, year, startage, endage, ageformat, 
			   causelist = conf[['causedist']])
{
	df <- data.frame()
	ctryalias <- conf[['countries']][[sprintf('%d', country)]][['alias']]
	sexalias <- conf[['sexes']][[sprintf('%d', sex)]][['alias']]
	casexlist <- Filter(function(x) conf[['causes']][[x]][['sex']] == 0 ||
			 conf[['causes']][[x]][['sex']] == sex, causelist) 
	for (cause in casexlist)
	{
		catrend <- agetrends.plot(country, cause, sex, year, year, 
					  startage, endage, 'perc', ageformat)
		df.catrend <- catrend$data
		df.catrend$cause <- cause
		df.catrend$caalias <- conf[['causes']][[cause]][['alias']]
		df <- rbind(df, df.catrend)
	}
	
	for (cause in casexlist)
	{
		causeconf = conf[['causes']][[cause]]
		if (causeconf[['classtot']])
		{
			for (subcause in casexlist)
			{
				subconf = conf[['causes']][[subcause]]
				if (!subconf[['classtot']] && 
				   subconf[['causeclass']] == causeconf[['causeclass']])
				{
					df$mort[df$cause == cause] <- 
						df$mort[df$cause == cause] - 
							df$mort[df$cause == subcause]
					df$caalias[df$cause == cause] <- 
						sprintf('%s övrigt', causeconf[['alias']])
				}
			}
		}

	}
	
	title <- sprintf('Fördelning dödsorsaker %s %s %d', sexalias, ctryalias, year)
	df.plot <- ggplot(data = df, aes(x = agealias, y = 100*mort, 
					 fill = caalias, group = caalias)) + 
		geom_area(alpha = 0.7, colour = 'black') + 
		xlab(agralias) + 
		ylab(percalias) + 
		scale_fill_hue(name = 'Orsak') + 
		scale_y_continuous(label = comma.lab) + 
		ggtitle(title) + 
		theme(axis.text.x = element_text(angle = 45), 
		      legend.position = 'bottom') +
                guides(fill = guide_legend(nrow = 3, byrow = TRUE))

	return(df.plot)
}

lgomp.test <- function(country, cause, sex, startyear, endyear, startage,  
			   endage, ageformat, type = 'rate', linear = FALSE, pc = 'p')
{
	if (pc == 'p')
	{
		yearcol = 'Year'
		yrseq <- sprintf('%d', seq(startyear, endyear))
	}
	else if (pc == 'c')
	{
		yearcol = 'cohort'
		yrseq <- sprintf('%d', seq(startyear - endage +5, 
					   endyear - startage - 5))
	}
	
	col.gomp <- function(x)
	{
		coef(lm(log(df.catrend.wide.yrs[[x]]) ~ df.catrend.wide$age, 
		   weights = sqrt(dno.wide[yrseq][[x]])))
	}
	col.gomp.nlslm <- function(x)
	{
		yr <- df.catrend.wide.yrs[[x]]
		age <- df.catrend.wide[['age']]
		wgths <- sqrt(dno.wide[yrseq][[x]])
		coef(nlsLM(yr ~ r0 * exp(alpha * age),
		   start = c(alpha = 0.14, r0 = exp(-18)), 
		   control = nls.lm.control(maxiter = 100), 
		   weights = wgths))
	}
	
	catrend <- agetrends.plot(country, cause, sex, startyear, endyear, 
			   startage, endage, type, ageformat)
	
	
	
	dno <- read.csv(sprintf('csv/%s%dno%d.csv', cause, country, sex))
	dno$Pop36sum <- rowSums(dno[sprintf('Pop%d', seq(3, 6))])
	dno$Pop2325sum <- rowSums(dno[sprintf('Pop%d', seq(23, 25))])
	popcols <- sprintf('Pop%s', c(seq(2, 25), '2325sum', '36sum'))
	dno.long <- gather(dno[c('Year', popcols)], ageorig, no, Pop2:Pop36sum)
	dno.merge <- merge(dno.long, catrend$data, c('Year', 'ageorig'))
	dno.wide <- spread_(dno.merge[c(yearcol, 'no', 'age')], yearcol, 'no')
	
	df.catrend <- catrend$data[c(yearcol, 'mort', 'age')]
	df.catrend.wide <- spread_(df.catrend, yearcol, 'mort')
	df.catrend.wide.yrs <- df.catrend.wide[yrseq]

	if (linear)
		list.gomp <- sapply(colnames(df.catrend.wide.yrs), 
				    col.gomp, simplify = FALSE)
	else
		list.gomp <- sapply(colnames(df.catrend.wide.yrs), 
				    col.gomp.nlslm, simplify = FALSE)
	df.gomp <- ldply(list.gomp)
	if (linear)
		colnames(df.gomp) <- c('Year', 'log_r0', 'alpha')
	rownames(df.gomp) <- df.gomp$Year
	if (!linear)
		df.gomp$log_r0 <- log(df.gomp$r0)

	long.gomp <- lm(log_r0 ~ alpha, data = df.gomp)


	return(list(fit = long.gomp, mort = df.catrend.wide, no = dno.wide))
}

