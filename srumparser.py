#!/usr/bin/python2 -O
#  -*- coding:utf-8 -*-

"""
    Parse SRUM database

    Author: David DURVAUX
    Copyright: EC DIGIT CSIRC (European Commission) - February 2017
"""
import os
import csv
import sys
import time
import argparse

# Install pyesedb with
#     $ python setup.py build
#     $ sudo python setup.py install
import pyesedb

# --------------------------------------------------------------------------- #

table_mapping = { # check values !!
    "WIN_NET_DATA_USAGE": "{973F5D5C-1D90-4944-BE8E-24B94231A174}",
    "ENERGY_USAGE": "{FEE4E14F-02A9-4550-B5CE-5FA2DA202E37}",
    "WPN_SRUM": "{D10CA2FE-6FCF-4F6D-848E-B2E99266FA86}"
    #"", "{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}"
    #"", "{DA73FB89-2BEA-4DDC-86B8-6E048C6DA477}"
    #"", "{DD6636C4-8929-4683-974E-22C046A43763}"
}

table_mapping_id = {} # will be filled later to map ID with key id

column_id_mapping = { # map the column type
    4  : "get_value_data_as_integer",  # Integer
    #8  : "",  # Timestamp
    15 : "get_value_data_as_integer"   # Apparently also integer
}

"""
    TEST
"""
def test():

    # Cygwin / Win location - "/cygdrive/c/Windows/System32/sru/SRUDB.dat"
    test_file = "./SRUDB.dat"

    print("TEST, libesedb version %s" % str(pyesedb.get_version()))
    print("Available functions: %s" % str(dir(pyesedb)))

    # Open DB file
    esedb_file = pyesedb.file()
    esedb_file.open(test_file)

    # listing tables
    numb_tables = esedb_file.get_number_of_tables()
    print("Numb of tables: %d" % numb_tables)
    for i in range(0,numb_tables):
        print("TABLE %d is called %s" % (i, esedb_file.get_table(i).get_name()))
        table_mapping_id[esedb_file.get_table(i).get_name()] = i
        print "Identifier: %d" % esedb_file.get_table(i).get_identifier()
        print "Number of records: %d" % esedb_file.get_table(i).get_number_of_records()
    
    # listing data from "WIN_NET_DATA_USAGE"
    print("DEBUG: key 1: %s" % table_mapping["WIN_NET_DATA_USAGE"])
    print("DEBUG: key 2: %s" % table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]])
    numb_records = esedb_file.get_table(table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]]).get_number_of_records()
    print("NUMBER OF RECORDS IN WIN_NET_DATA_USAGE = %d" % numb_records)

    columns = []
    values = []
    # printing records
    for i in range(0, numb_records):

        print("Parsing record %d  out of %d" % (i, numb_records))

        record = esedb_file.get_table(table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]]).get_record(i)
        numb_vals = record.get_number_of_values()
        row = {}

        for j in range(0, numb_vals):
            col_name = esedb_file.get_table(table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]]).get_record(i).get_column_name(j)
            if(i == 0): # only initialize list of columns once
                columns.append(col_name)
            col_type = esedb_file.get_table(table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]]).get_record(i).get_column_type(j)
            long_val = esedb_file.get_table(table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]]).get_record(i).is_long_value(j)
            multi_val = esedb_file.get_table(table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]]).get_record(i).is_multi_value(j)

            col_value_data = esedb_file.get_table(table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]]).get_record(i).get_value_data(j)
            # try to read the data as the correct type
            if col_type in column_id_mapping.keys():
                func = getattr(esedb_file.get_table(table_mapping_id[table_mapping["WIN_NET_DATA_USAGE"]]).get_record(i), column_id_mapping[col_type])
                col_value_data = func(j)
            #elif col_type == 8: #Timestamp, requires decoding
            #    col_value_data = float(col_value_data)
            #    col_value_data = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(col_value_data))
            else:
                col_value_data = col_value_data.encode('hex')

            #print("Col name: %s Type: %s Value: %s (long: %s / multi: %s)" % (col_name, col_type, col_value_data, long_val, multi_val))
            row[col_name] = col_value_data
        values.append(row)

    # close connection and return
    esedb_file.close()
    return (columns, values)

# --------------------------------------------------------------------------- #

def __get_data_from_table(table):
    return

"""
    Main function
"""
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database', action='store', dest='database', help='Path to SRUM database.  By default, C:\\Windows\\System32\\sru\\SRUDB.dat')
    #parser.add_argument('-H', '--history', action='store', dest='history', help='Path to JSON history file.  By default, ./history.json', default='./history.json')

    # Parse arguments and configure the script
    arguments = parser.parse_args()
    if arguments.database:
        if not os.path.isfile(arguments.database):
            print("ERROR: %s has to be an existing file!" % arguments.database)
            parser.print_help()
            sys.exit(-1)
        else:
            print("DEBUG - do something")

    # TEST
    (columns, values) = test()
    with open('test_data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = columns)
        writer.writeheader()
        writer.writerows(values)

    # All done ;)
    return

# --------------------------------------------------------------------------- #

"""
   Call main function
"""
if __name__ == "__main__":
    
    # Create an instance of the Analysis class (called "base") and run main 
    main()

# That's all folks ;)
