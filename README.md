# Linux_process_monitor


Creates a daemon that collects cpu, memory and io usage of running processes into a database.
The database is then used to create two statistical reports: 
a) A report displaying average, max, median and 95% percentile of cpu, memory and io usage for each process
b) A report showing top N processes with the highest values for all the statistics-metric combinations
There are some customization options available in 'configuration.py' to set how the database and
reports are put together.


HOW TO USE:
1) Configure settings in configuration.py. Please follow the format instructions
as I haven't been trying to catch errors stemming from incorrect configuration imput.

2) Run main.py with 'start' argument to start the daemon.
(python3 main.py start)
stop, restart and status arguments can be used as well

3) Run reporting.py to create reports.


###### Main libraries used: psutil, pandas, daemonocle
