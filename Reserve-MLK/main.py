#!/usr/bin/env python

from datetime import datetime
import argparse
import sys

def get_date():
	"""
	Get today's date in YYYYMMDD format
	"""
	return str(datetime.now()).split()[0].replace('-', '')

def get_time():
	"""
	Get current time hour + 1
	"""
	hour = str(datetime.now()).split()[1].replace(':', '')[:2]
	
	return str(int(hour) + 1)	# Round up to next hour

if __name__ == '__main__':
	parser =  argparse.ArgumentParser(description="Dont waste time reserving study rooms again!!!")

	parser.add_argument('filename', help="Input text file of ID PIN")
	parser.add_argument('-r', '--room', help="Room number", nargs='?')
	parser.add_argument('-d', '--day', help="Day to book in this yyyymmdd format", nargs='?', default=get_date())
	parser.add_argument('-t', '--time', help="Starting time (int)[0-23]", nargs='?', default=get_time())
	parser.add_argument('-a', '--all', help="Set to 24 hour mode", action='store_true')
	parser.add_argument('-q', '--query', help="Set to query only", action='store_true')

	if len(sys.argv) < 3:			# Valid number arguments?
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()		# Parse input arguments

	if args.query:
		import Querier
		Querier.query_list(args.filename, args.room)

		sys.exit(0)

	###########################

	globals()['24hr'] = args.all	# Set global variable

	if args.filename and args.room and args.time:
		import Attacker
		Attacker.begin( args.filename, args.room, args.day, args.time )
	
	else:
		parser.print_help()
		sys.exit(1)
