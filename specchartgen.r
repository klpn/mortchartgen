library(ggplot2)
library(tidyr)
library(yaml)
library(XML)
library(gridSVG)
library(rjson)

sexratio.trends.plot<-function(country,cause,sex1,sex2,startyear,endyear,startage,endage,type,ageformat)
{
	conf<-yaml.load_file('chartgen.yaml')
	sex1alias<-conf[['sexes']][[sex1]][['alias']]
	sex2alias<-conf[['sexes']][[sex2]][['alias']]
	sex1<-agetrends.plot(country,cause,sex1,startyear,endyear,startage,endage,type,ageformat)
	sex2<-agetrends.plot(country,cause,sex2,startyear,endyear,startage,endage,type,ageformat)
	title<-gsub(sex1alias,sprintf('%s/%s',sex1alias,sex2alias),sex1$labels$title)
	df<-sex1$data
	df$ratio<-sex1$data$mort/sex2$data$mort
	df.plot<-ggplot(data=df,aes(x=Year,y=ratio,group=agealias,colour=agealias))+xlab('År')+ylab('Kvot')+ggtitle(title)+geom_point()+geom_smooth()+scale_colour_discrete(name='Åldersgrupp')+theme(axis.text.x=element_text(angle=45))
	return(df.plot)
}


agetrends.plot<-function(country,cause,sex,startyear,endyear,startage,endage,type,ageformat)
{
	conf<-yaml.load_file('chartgen.yaml')
	csvname<-sprintf('csv/%s%d%s%d.csv',cause,country,type,sex)
	df<-read.csv(csvname,header=TRUE)
	caalias<-conf[['causes']][[cause]][['alias']]
	ctryalias<-conf[['countries']][[sprintf('%d',country)]][['alias']]
	sexalias<-conf[['sexes']][[sex]][['alias']]
	age<-c(seq(5,95,by=5),85)
	agealias<-sprintf('%d\u2013%s',age,c(seq(9,94,by=5),'w','w'))
	ageorig<-sprintf('Pop%s',c(seq(7,25),'2325sum'))
	ages<-data.frame(age,agealias,ageorig)

	if(type=='rate')
	{
	       	typealias<-'Dödstal'
		yl<-'log(dödstal)'
		yfunc<-quote(log(mort))
	}
	if(type=='perc')
	{       
		typealias<-'Andel dödsfall'
	       	yl<-'%'
		yfunc<-quote(100*mort)
	}
	title<-sprintf('%s %s %s %s',typealias,caalias,sexalias,ctryalias)


	if(ageformat==0) df.long<-gather(df,ageorig,mort,Pop7:Pop25)
	else if(ageformat==1) df.long<-gather(subset(df,select=c(Year,Pop7:Pop22,Pop2325sum)),ageorig,mort,Pop7:Pop2325sum)
	df.long<-merge(df.long,ages,'ageorig')
	df.long.sub<-subset(df.long,Year>=startyear & Year<=endyear & age %in% seq(startage,endage,by=5))
	env<-environment()

	df.plot<-ggplot(data=df.long.sub,aes(x=Year,y=eval(yfunc),group=agealias,colour=agealias),environment=env)+xlab('År')+ylab(yl)+ggtitle(title)+geom_point()+geom_smooth()+scale_colour_discrete(name='Åldersgrupp')+theme(axis.text.x=element_text(angle=45))

	return(df.plot)
}

ctriesyr.batchplot<-function(compyrseq=seq(1952,2012,by=10))
{
	conf<-yaml.load_file('chartgen.yaml')
	causenames<-names(conf[['causes']])
	agenames<-names(conf[['ages']])
	svgdir<-'mortchart-site/charts/ctriesyr'
	xmlprefix<-'<?xml version="1.0" encoding="UTF-8"?>\n'
	dir.create(svgdir,showWarnings=FALSE)
	
	for(year in compyrseq)
	{
		for(cause in causenames)
		{
			causeconf<-conf[['causes']][[cause]]
			if(!(year %in% causeconf[['skipyrs']])){
			for(age in agenames)
			{
				
				if(!(age %in% causeconf[['skip']]))
				   {
					   type<-conf[['ages']][[age]][['ptype']]
					   if(!(cause=='all' & type=='perc')){
					   svgpath<-sprintf('%s/%s%s%scomp%d.svg',svgdir,cause,type,age,year)
					   curgrid<-ctriesyr.plot(cause,year,age,type)
					   print(curgrid)
					   if(causeconf[['sex']]==0)
					   {
					   curgrid.svg<-grid.export(addClasses=TRUE)
					   cat(xmlprefix,gsub('</svg>$','',saveXML(curgrid.svg$svg)),svgscript(curgrid$data),file=svgpath)
					   }
					   else grid.export(svgpath)
					   dev.off()

					   }
				   }
			}}
		}
	}

}

svgscript<-function(graphdata)
{
	notice<-'<!-- Adapted from http://timelyportfolio.github.io/gridSVG_intro/ -->'
	d3.script<-'<script xlink:href="http://d3js.org/d3.v3.js"></script>'
	jsonarr<-rjson::toJSON(apply(graphdata,MARGIN=1,FUN=function(x)return(list(x))))
	dataarr.script<-sprintf('var dataarr=%s;',jsonarr)
	datamap.script<-'var dataToBind = d3.entries(dataarr.map(function(d,i) {return d[0]}));'
	databind.script<-'var scatterPoints = d3.select(".points").selectAll("use");\nscatterPoints.data(dataToBind);'
	tool.script<-'scatterPoints  
    .on("mouseover", function(d) {      
      //Create the tooltip label
      var tooltip = d3.select(this.parentNode).append("g");
      tooltip
        .attr("id","tooltip")
       tooltip.append("text")
        .attr("transform","scale(1,-1)")
        .attr("x",100)
        .attr("y",-600)
        .attr("text-anchor","start")
        .attr("stroke","gray")
        .attr("fill","gray")      
        .attr("fill-opacity",1)
        .attr("opacity",1)
        .text(d.value.countryalias + ":");       
      tooltip.append("text")
        .attr("transform","scale(1,-1)")
        .attr("x",100)
        .attr("y",-580)
        .attr("text-anchor","start")
        .attr("stroke","gray")
        .attr("fill","gray")
        .attr("fill-opacity",1)
        .attr("opacity",1)
        .text("kv: " + d.value.femmort.replace(".",","));
      tooltip.append("text")
        .attr("transform","scale(1,-1)")
        .attr("x",100)
        .attr("y",-560)
        .attr("text-anchor","start")
        .attr("stroke","gray")
        .attr("fill","gray")      
        .attr("fill-opacity",1)
        .attr("opacity",1)
        .text("m: " + d.value.malemort.replace(".",","));
    })              
    .on("mouseout", function(d) {       
        d3.select("#tooltip").remove();  
    });'
   return(sprintf('%s\n%s\n<script>\n%s\n%s\n%s\n%s\n</script>\n</svg>',notice,d3.script,dataarr.script,datamap.script,databind.script,tool.script))

}

ctriesyr.plot<-function(cause,compyear,ageorig,type)
{
	conf<-yaml.load_file('chartgen.yaml')
	ctrynames<-names(conf[['countries']])
	sex<-as.numeric(conf[['causes']][[cause]][['sex']])
	caalias<-conf[['causes']][[cause]][['alias']]
	agealias<-conf[['ages']][[ageorig]][['alias']]
	if('note' %in% names(conf[['ages']][[ageorig]])) agealias<-sprintf('%s (%s)',agealias,conf[['ages']][[ageorig]][['note']])

	if(type=='rate') typealias<-'Dödstal'
	else if(type=='perc') typealias<-'Andel dödsfall'
	if(sex==1) sexalias<-'män'
	else if(sex==2) sexalias<-'kvinnor'
	
	df<-data.frame()
	for(country in ctrynames)
	{
		if(sex==0)
		{
			csvname.country.male<-sprintf('csv/%s%s%s1.csv',cause,country,type)
			csvname.country.fem<-sprintf('csv/%s%s%s2.csv',cause,country,type)
			df.country.male<-read.csv(csvname.country.male,header=TRUE)
			df.country.fem<-read.csv(csvname.country.fem,header=TRUE)
			df.country<-data.frame(Year=df.country.male$Year)
			df.country['malemort']<-df.country.male[ageorig]
			df.country['femmort']<-df.country.fem[ageorig]
		}
		else
		{
			csvname.country<-sprintf('csv/%s%s%s%d.csv',cause,country,type,sex)
			df.country.0<-read.csv(csvname.country,header=TRUE)
			df.country<-data.frame(Year=df.country.0$Year)
			df.country['mort']<-df.country.0[ageorig]
		}
		df.country$country<-country
		df.country$countryalias<-conf[['countries']][[country]][['alias']]
		df.country$countryiso<-conf[['countries']][[country]][['iso3166']]
		df<-rbind(df,df.country)
	}
	df.sub<-subset(df,Year==compyear)
	rownames(df.sub)<-NULL
	comma.lab<-function(x){format(x,decimal.mark=',')}

	if(sex==0)
	{
		title<-sprintf('%s %s\n%s %d',typealias,caalias,agealias,compyear)
		df.plot<-ggplot(data=df.sub,aes(x=femmort,y=malemort))+xlab(sprintf('%s kvinnor',typealias))+ylab(sprintf('%s män',typealias))+scale_x_continuous(label=comma.lab)+scale_y_continuous(label=comma.lab)+ggtitle(title)+geom_text(aes(label=countryiso),size=3.5,alpha=1/2)+geom_point(alpha=1/8,size=4)
	}
	else
	{
		title<-sprintf('%s %s %s %s %d',typealias,caalias,sexalias,agealias,compyear)
		df.plot<-ggplot(data=df.sub,aes(x=countryalias,y=mort))+xlab('Befolkning')+ylab(typealias)+scale_y_continuous(label=comma.lab)+ggtitle(title)+geom_bar(stat='identity')+theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
	}
	
	return(df.plot)
	
}
