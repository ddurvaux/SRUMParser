#!/usr/bin/python2 -O
#  -*- coding:utf-8 -*-

"""
    Parse SRUM database

    Author: David DURVAUX
    Copyright: EC DIGIT CSIRC (European Commission) - February 2017

    Version 0.1
    TODO
        - parse timestamp
        - check all tables
        - link some table object with registry info
"""
import os
import csv
import sys
import time
import struct
import argparse
from datetime import datetime,timedelta

# Install pyesedb with
#     $ python setup.py build
#     $ sudo python setup.py install
try:
    import pyesedb
except:
    print("Please install pyesedb from https://github.com/libyal/libesedb")

try:
    from Registry import Registry
except:
    print("Please install python-registry from https://github.com/williballenthin/python-registry")


# --------------------------------------------------------------------------- #

class SRUMDB:
    """
        Handle the SRUM DB in ESE format

        Format date:
        https://blogs.msdn.microsoft.com/oldnewthing/20030905-02/?p=42653
    """

    table_mapping = { # check and complete values !!
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

    srumdb = None


    def __init__(self, srumdbpath="C:\\Windows\\System32\\sru\\SRUDB.dat"):
        try:
            self.srumdb =  pyesedb.file()
            self.srumdb.open(srumdbpath)
            self.__set_table_mapping__()
        except Exception as e:
            print("Impossible to open SRUM DB: %s" % srumdbpath)
            print(e)
        return


    def getTablesFromDB(self):
        numb_tables = self.srumdb.get_number_of_tables()
        name2id = {}
        for i in range(0,numb_tables):
            name2id[self.srumdb.get_table(i).get_name()] = i
        return name2id


    def __set_table_mapping__(self):
        self.table_mapping_id = self.getTablesFromDB()
        return


    def getDataFromTable(self, tablename="WIN_NET_DATA_USAGE", limit=0):
        numb_records = self.srumdb.get_table(
            self.table_mapping_id[
                self.table_mapping[tablename]]).get_number_of_records()
        columns = []
        values = []

        # only retrieve the first limit event
        if limit != 0:
            numb_records = limit

        # dump required events (all if limit = 0 or the first limit events)
        for i in range(0, numb_records):
            print("Parsing record %d  out of %d" % (i, numb_records))
            record = self.srumdb.get_table(self.table_mapping_id[self.table_mapping[tablename]]).get_record(i)
            numb_vals = record.get_number_of_values()
            row = {}

            for j in range(0, numb_vals):
                col_name = self.srumdb.get_table(self.table_mapping_id[self.table_mapping[tablename]]).get_record(i).get_column_name(j)
                if(i == 0): # only initialize list of columns once
                    columns.append(col_name)
                col_type = self.srumdb.get_table(self.table_mapping_id[self.table_mapping[tablename]]).get_record(i).get_column_type(j)
                long_val = self.srumdb.get_table(self.table_mapping_id[self.table_mapping[tablename]]).get_record(i).is_long_value(j)
                multi_val = self.srumdb.get_table(self.table_mapping_id[self.table_mapping[tablename]]).get_record(i).is_multi_value(j)
                col_value_data = self.srumdb.get_table(self.table_mapping_id[self.table_mapping[tablename]]).get_record(i).get_value_data(j)

                # try to read the data as the correct type
                if col_type in self.column_id_mapping.keys():
                    func = getattr(self.srumdb.get_table(
                        self.table_mapping_id[self.table_mapping[tablename]]).get_record(i), self.column_id_mapping[col_type])
                    col_value_data = func(j)
                elif col_type == 8: #Timestamp, requires decoding
                    col_value_data = ole64doubleTOtimestamp(struct.unpack('<d', col_value_data)[0])
                else:
                    print("DEBUG: %s type: %s" % (col_value_data, type(col_value_data)))
                    col_value_data = col_value_data.encode('hex')

                #print("Col name: %s Type: %s Value: %s (long: %s / multi: %s)" % (col_name, col_type, col_value_data, long_val, multi_val))
                row[col_name] = col_value_data
            values.append(row)

        return [columns, values]


    def close(self):
        if self.srumdb is not None:
            self.srumdb.close()
        return

# --------------------------------------------------------------------------- #

class SRUMRegistry:
    """
        Handle the SRUM info stored in the registry

            - AppID check https://msdn.microsoft.com/fr-fr/library/windows/desktop/aa367566(v=vs.85).aspx
               (HKEY_CLASSES_ROOT\AppID\) TBC
            - Interface ID (SOFTWARE\Microsoft\WlanSvc\Interfaces)
    """
    software = None

    def __init__(self, software="./SOFTWARE"):
        try:
            self.software = Registry.Registry(software)
        except Exception as e:
            print("Impossible to open registry file")
            print(e)
        return


    def getInterfacesId(self):
        try:
            interface = self.software.open('Microsoft\\WlanSvc\\Interfaces')
        except Exception as e:
            print("No wireless interface found")
            print(e)
        return



# --------------------------------------------------------------------------- #

def ole64doubleTOtimestamp(oleval):
    """
        OLE date are represented as 64 bits float.
        the value is a fractional value of days since
        30/12/1899 00:00:00

        oleval passed as a 64 bits float (python default float type)
    """
    OLE_TIME_ZERO = datetime(1899, 12, 30, 0, 0, 0)
    try:
        return OLE_TIME_ZERO + timedelta(days=oleval)
    except Exception as e:
        print("Impossible to parse date: %d" % oleval)
        print(e)
        return None

"""
    TEST
"""
def test():
    test_file = "./SRUDB.dat"
    srumdb = SRUMDB(test_file)
    result = srumdb.getDataFromTable("WIN_NET_DATA_USAGE", 10)
    srumdb.close()
    return result

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
        writer = csv.DictWriter(csvfile, fieldnames = columns, dialect="excel")
        writer.writeheader()
        writer.writerows(values)
        csvfile.close()

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