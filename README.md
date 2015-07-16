#mortchartgen
`mortchartgen` is a tool which is used to create charts of mortality trends for different countries, age groups and causes of death based on data from WHO Mortality Database. The tool uses Pandas and matplotlib to generate the charts and stores the data in a MySQL database. A YAML configuration file is used to specify the charts to be generated.

I use the tool to generate charts for the website [Mortalitetsdiagram](http://mortchart.klpn.se) ("mortality charts"). Files for this site (excluding the SVG charts themselves) are included in the subdirectory `site`. Currently, the generated charts are in Swedish. I am not affiliated with WHO, and they are not responsible for any interpretations of mortality trends based on charts generated from the tool. The tool is licensed under an [ISC license](LICENSE).

##Setup
It is assumed that you have a working Python setup, as well as access to a MySQL/MariaDB server, with a user privileged to create databases. The unzipped data files will require about 500 MB of disk space. The script `download.py` imports `requests`, `shutil`, `os` and `zipfile`, `tableimp.py` imports `os` and `subprocess`, and the main script, `chartgen.py`, imports `mysql`, `pandas`, `matplotlib`, `yaml`, `os` and `time`.

1. Run `download.py [directory]` in order to download the data files and documentation from the WHO website and unzip them into `directory`.
2. Read the SQL file `setupdb.sql` into the MySQL client, e.g. `mysql --defaults-extra-file=tableimp.cnf < setupdb.sql`. This will create a database `Morticd` with two tables, `Pop` and `Deaths`, as well as a user `whomuser` with select rights granted on these tables, which is used for the SQL queries in the chart generator.You can use the provided file `tableimp.cnf` in this step and the next, as shown in the example, but then you have to adjust the relevant settings in the file (e.g. user, password, host and socket) in order for the database connection to work.  For more information about the fields in the tables, consult the WHO documentation.
3. Load the unzipped data files into the newly created tables. The file `pop` should be loaded into the table `Pop`, and the files with names starting with `Mort` should all be loaded into the table `Deaths`. The script `tableimp.py` loops through the data files and reads them into the tables using `mysqlimport`. You can call the script with `tableimp.py [directory]`, where `directory` is the download directory specified in step 1. The default configuration is to read the files locally from the client, and this has to be supported by the MySQL server. Otherwise, move the files into a location where the server can read them directly and remove the `local` option in `tableimp.cnf`.

##Generate the charts
Call the function `batchplot()` in `chartgen.py` in order to generate the charts. This function is automatically called if `chartgen.py` is invoked from the system shell. The charts are saved as SVG files in the subdirectory `site/charts`. If you want to skip certain countries, age groups or causes of death, comment out the relevant lines in `chartgen.yaml`. Some values in the dictionary `conn_config` (now read from `settings` in `chartgen.yaml`) may also have to be changed in order for the database connection to work. In particular, you should change `host` and `unix_socket` to suit your MySQL server.

##Generate the site
By running `indexgen.py` you can generate `site/index.html` based on the settings in `chartgen.yaml` and the template `sitetempl/index.jinja` (which uses [Jinja2](https://github.com/mitsuhiko/jinja2)).

##Generate docs
Run `make pdfbib` in `docs` in order to generate PDF documentation from the Markdown source. This requires a LaTeX distribution as well as [pandoc](https://github.com/jgm/pandoc) (in order to convert Markdown). Run `make html` to generate HTML documentation using pandoc.

##CSV generation
If `savecsv` under `settings` in `chartgen.yaml` is `true`, `chartgen.py` will save the dataframes used to generate the charts as CSV files in the subdirectory `csv`, so that they can be further analysed in other programs.

The R script `specchartgen.r` demonstrates how the generated CSV files can be used. It contains the functions `agetrends.plot` which generates charts showing secular trends for a given combination of sex, cause and a interval of 5-year age groups, `sexratio.trends.plot` which generates charts showing secular trends for sex ratios for mortality rates/percentages, and `ctrisyear.plot` which generates charts giving a comparison of mortality between countries for a given cause and year. It can generate scatterplots of female vs male mortality or bar charts for a single sex. The function `ctriesyr.batchplot` uses `ctrisyear.plot` to generate charts for all causes and age groups in `chartgen.yaml` and for all years in a given sequence and export these as SVG files in the subdirectory `site/charts/ctriesyr`. All these charts are generated using [ggplot2](https://github.com/hadley/ggplot2), and the script also uses the packages [tidyr](https://github.com/hadley/tidyr),  [yaml](http://cran.r-project.org/web/packages/yaml), [XML](http://cran.r-project.org/web/packages/XML), [gridSVG](https://sjp.co.nz/projects/gridsvg) and [rjson](http://cran.r-project.org/web/packages/rjson).
