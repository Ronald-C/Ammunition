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
	parser =  argparse.ArgumentParser()

	parser.add_argument("-f", "--file", help="input file of ID PIN", nargs=1)
	parser.add_argument("-r", "--room", help="room number", nargs=1)
	parser.add_argument("-d", "--day", help="day to book in this yyyymmdd format", nargs='?', default=get_date())
	parser.add_argument("-t", "--time", help="Starting time (int)[0-23]", nargs='?', default=get_time())

	if len(sys.argv) < 5:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()

	if args.file and args.room and args.time:
		Attacker.usingFile( args.file[0], args.room[0], args.day, args.time )
	else:
		sys.exit(1)