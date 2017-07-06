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