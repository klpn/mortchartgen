library(ggplot2)
library(tidyr)
library(yaml)

agetrends.plot<-function(country,cause,sex,startyear,endyear,startage,endage,type,ageformat)
{
	conf<-yaml.load_file('chartgen.yaml')
	csvname<-sprintf('csv/%s%d%s%d.csv',cause,country,type,sex)
	df<-read.csv(csvname,header=TRUE)
	caalias<-conf[['causes']][[cause]][['alias']]
	ctryalias<-conf[['countries']][[sprintf('%d',country)]][['alias']]
	age<-c(seq(5,95,by=5),85)
	agealias<-sprintf('%d\u2013%s',age,c(seq(9,94,by=5),'w','w'))
	ageorig<-sprintf('Pop%s',c(seq(7,25),'2325sum'))
	ages<-data.frame(age,agealias,ageorig)

	if(sex==1) sexalias<-'män'
	else if(sex==2) sexalias<-'kvinnor'
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

	df.plot<-ggplot(data=df.long.sub,aes(x=Year,eval(yfunc),group=agealias,colour=agealias),environment=env)+xlab('År')+ylab(yl)+ggtitle(title)+geom_point()+geom_line()+scale_colour_discrete(name='Åldersgrupp')+theme(axis.text.x=element_text(angle=45))

	return(df.plot)
}

ctriesyr.batchplot<-function(compyrseq=seq(1952,2012,by=10))
{
	conf<-yaml.load_file('chartgen.yaml')
	causenames<-names(conf[['causes']])
	agenames<-names(conf[['ages']])
	svgdir<-'site/charts/ctriesyr'
	dir.create(svgdir,showWarnings=FALSE)
	
	for(year in compyrseq)
	{
		for(cause in causenames)
		{
			for(age in agenames)
			{
				
				if((age %in% conf[['causes']][[cause]][['skip']])==FALSE)
				   {
					   type<-conf[['ages']][[age]][['ptype']]
					   if(!(cause=='all' & type=='perc')){
					   svgpath<-sprintf('%s/%s%s%scomp%d.svg',svgdir,cause,type,age,year)
					   svg(svgpath)
					   print(ctriesyr.plot(cause,year,age,type))
					   dev.off()
					   }
				   }
			}
		}
	}

}


ctriesyr.plot<-function(cause,compyear,ageorig,type)
{
	conf<-yaml.load_file('chartgen.yaml')
	ctrynames<-names(conf[['countries']])
	sex<-as.numeric(conf[['causes']][[cause]][['sex']])
	caalias<-conf[['causes']][[cause]][['alias']]
	agealias<-conf[['ages']][[ageorig]][['alias']]
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
		df<-rbind(df,df.country)
	}
	df.sub<-subset(df,Year==compyear)
	comma.lab<-function(x){format(x,decimal.mark=',')}

	if(sex==0)
	{
		title<-sprintf('%s %s %s %d',typealias,caalias,agealias,compyear)
		df.plot<-ggplot(data=df.sub,aes(x=femmort,y=malemort))+xlab(sprintf('%s kvinnor',typealias))+ylab(sprintf('%s män',typealias))+scale_x_continuous(label=comma.lab)+scale_y_continuous(label=comma.lab)+ggtitle(title)+geom_point(shape=1)+geom_text(aes(label=countryalias),size=3.5,alpha=1/2)
	}
	else
	{
		title<-sprintf('%s %s %s %s %d',typealias,caalias,sexalias,agealias,compyear)
		df.plot<-ggplot(data=df.sub,aes(x=countryalias,y=mort))+xlab('Befolkning')+ylab(typealias)+scale_y_continuous(label=comma.lab)+ggtitle(title)+geom_bar(stat='identity')+theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
	}
	
	return(df.plot)
	
}
