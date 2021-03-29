# database
# time period X in seconds between process data collections, sleep used
main_X = 10
# top N processes number for the collection, 0 = all processes are collected
main_N = 0

# reporting
# list of process names to create the reports for
# blank list = all processes are used
process_list = []
# time period from - filters the database records
# enter either datetime in format 'yyyy-mm-dd hh:mm:ss'
# or a falsy value in case you don't want to use this filter('', 0...)
reporting_from = ''
# time period to - same functionality and format rules as for reporting_from
reporting_to = ''
# top N processes number for the report2
report2_N = 5
