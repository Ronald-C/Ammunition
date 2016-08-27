from argparse import ArgumentParser
from sys import argv, exit

from source import singular, batch

def main():
	parser = ArgumentParser(description='Study room reserver')
	parser.add_argument('-f', '--filename', nargs=1, help='CSV file of ID and PIN')
	
	args = parser.parse_args()
	print len(argv)
	if len(argv) > 3 and argv[0] != '-c':
		parser.print_help()
		exit(1)

	if args.filename is None:
		singular()

	else:
		batch(args.filename)

if __name__ == '__main__':
    main()