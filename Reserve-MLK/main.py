from datetime import datetime
import argparse
import sys

import Attacker

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

	parser.add_argument('file', help="input file of ID PIN")
	parser.add_argument('room', help="room number")
	parser.add_argument('-a', '--all', help="24 hour mode", action='store_true')
	parser.add_argument('-d', '--day', help="day to book1 in this yyyymmdd format", nargs=1, default=get_date())
	parser.add_argument('-t', '--time', help="Starting time (int)[0-23]", nargs=1, default=get_time())

	if len(sys.argv) < 3:			# Valid number arguments?
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()		# Parse input arguments

	globals()['24hr'] = args.all	# Set global variable

	if isinstance(args.time, list):		# optional args == list() unlike default
		args.time = args.time[0]

	if isinstance(args.day, list):
		args.day = args.day[0]

	if args.file and args.room and args.time:
		Attacker.usingFile( args.file, args.room, args.day, args.time )
	else:
		parser.print_help()
		sys.exit(1)
