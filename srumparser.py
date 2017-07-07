#!/usr/bin/python2 -O
#  -*- coding:utf-8 -*-

"""
	Parse SRUM database

	Author: David DURVAUX
	Copyright: EC DIGIT CSIRC (European Commission) - February 2017
"""
import os
import sys
import argparse

# Add path to pyesedb
sys.path.append("/Users/david/Workspace/git/libesedb-20170121")
import pyesedb

# --------------------------------------------------------------------------- #

__table_mapping = { # check values !!
    "WIN_NET_DATA_USAGE", "{973F5D5C-1D90-4944-BE8E-24B94231A174}"
    "ENERGY_USAGE", "{FEE4E14F-02A9-4550-B5CE-5FA2DA202E37}"
    "WPN_SRUM", "{D10CA2FE-6FCF-4F6D-848E-B2E99266FA86}"
    #"", "{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}"
    #"", "{DA73FB89-2BEA-4DDC-86B8-6E048C6DA477}"
    #"", "{DD6636C4-8929-4683-974E-22C046A43763}"
}

"""
	TEST
"""
def test():

    # Cygwin / Win location - "/cygdrive/c/Windows/System32/sru/SRUDB.dat"
    test_file = "./test/SRUDB.dat"

    print("TEST, libesedb version %s" % str(pyesedb.get_version()))

    # Open DB file
    esedb_file = pyesedb.file()
    esedb_file.open(test_file)

    numb_tables = esedb_file.get_number_of_tables()
    print("Numb of tabbles: %d" % numb_tables)
    for i in range(0,numb_tables):
        print("TABLE %d is called %s" % (i, esedb_file.get_table(i).get_name()))
    esedb_file.close()

    return

# --------------------------------------------------------------------------- #

"""
    Main function
"""
def main():
	# Parse command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--database', action='store', dest='database', help='Path to SRUM database.  By default, C:\\Windows\\System32\\sru\\SRUDB.dat')
	#parser.add_argument('-H', '--history', action='store', dest='history', help='Path to JSON history file.  By default, ./hstory.json', default='./history.json')

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
	test()

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