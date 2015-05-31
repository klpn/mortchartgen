#mortchartgen
`mortchartgen` is a tool which is used to create charts of mortality trends for different countries, age groups and causes of death based on data from WHO Mortality Database. The tool uses Pandas and matplotlib to generate the charts and stores the data in a MySQL database. A YAML configuration file is used to specify the charts to be generated.

I use the tool to generate charts for the website [Mortalitetsdiagram](http://mortchart.klpn.se). Files for this site (excluding the SVG charts themselves) are included in the subdirectory `site`. Currently, the generated charts are in Swedish.

##Setup
It is assumed that you have a working Python setup, as well as access to a MySQL/MariaDB server, with a user privileged to create databases. The unzipped data files will require about 500 MB of disk space. The script `download.py` imports `requests`, `shutil`, `os` and `zipfile`, and the main script, `chartgen.py`, imports `mysql`, `pandas`, `matplotlib`, `yaml` and `time`.

1. Run `download.py <directory>` in order to download the data files and documentation from the WHO website and unzip them into `directory`.
2. Read the SQL file `setupdb.sql` into the MySQL client, e.g. `mysql -u root -p[password] < setupdb.sql`. This will create a database `Morticd` with two tables, `Pop` and `Deaths`, as well as a user `whomuser` with select rights granted on these tables, which is used for the SQL queries in the chart generator. For more information about the fields in the tables, consult the WHO documentation.
3. Load the unzipped data files into the newly created tables. The file `Pop` should be loaded into the table `Pop`, and the files with names starting with `Morticd` should all be loaded into the table `Deaths`. The script `tableimp.py` loops through the data files and reads them into the tables using `mysqlimport`. You have to adjust the settings in `tableimp.cnf` (e.g. user, password, host and socket) in order for this to work. The default configuration is to read the files locally from the client, and this has to be supported by the MySQL server. Otherwise, move the files into a location where the server can read them directly and remove the `local` option in `tableimp.cnf`.

##Generate the charts
Call the function `batchplot()` in `chartgen.py` in order to generate the charts. The charts are saved as SVG files in the subdirectory `site/charts`. If you want to skip certain countries, age groups or causes of death, comment out the relevant lines in `chartgen.yaml`. Some values in the dictionary `conn_config` in `chartgen.py` may also have to be changed in order for the database connection to work. In particular, you should change `host` and `unix_socket` to suit your MySQL server.
