import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADER = { 'User-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36', 
	'Content-Type': 'application/x-www-form-urlencoded', 'Upgrade-Insecure-Requests': 1, 'Referer': 'http://libonline.sjlibrary.org/public/login.aspx', 'Connection':'keep-alive' }
LOGIN_URL = 'http://libonline.sjlibrary.org/public/login.aspx'

HOURS = ['0000', '0100', '0200', '0300', '0400', '0500', '0600', '0700', '0800', '0900', '1000', '1100', 
	'1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900', '2000', '2100', '2200', '2300']


def attack(_idNumber, _pinNumber, _room_number, _day, _timeStart, _timeEnd):
	with requests.Session() as r:
		
		################ LOGIN LANDING PAGE ################
		response = r.get(LOGIN_URL, headers=HEADER)

		soup = BeautifulSoup(response.text, 'html.parser')
		# Get required view states for login
		viewState = soup.find('input', attrs={'name': '__VIEWSTATE' }).get('value')
		viewStateGen = soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'}).get('value')
		eventValidation = soup.find('input', attrs={'name': '__EVENTVALIDATION'}).get('value') 

		params = {'txtCardno': _idNumber, 'txtPin': _pinNumber, 'btnLogin': 'Sign-in', 'hidPINTextboxVisbleState': 'show',
			'hidCardNoPrefix': '', '__VIEWSTATE': viewState, '__VIEWSTATEGENERATOR': viewStateGen, '__EVENTVALIDATION': eventValidation}



		return True

def isValid(line):
	return line.replace(' ', '').isdigit()

def nonblank_lines(file):
	"""
	Generator to validate every file line entry
	"""
	for line in file:
		line = str(line).strip()
		if line and isValid(line):
			yield line
		else:
			print "[Warning] Empty entry found"


def usingFile(filename, room_number, day, time):
	"""
	Loop through entries and attack
	"""
	day = str(datetime.strptime(day, '%Y%m%d')).split()[0]
	time = int(time)
	try:

		with open(filename, 'r+') as file:
			
			for line in nonblank_lines(file):
				idNumber, pinNumber = [ entry for entry in line.split() ]

				timeStart = HOURS[time]
				timeEnd = HOURS[time + 1]

				if(timeStart == '2000'):	
					timeEnd = '2055'

				# Register user
				if attack(idNumber, pinNumber, room_number, day, timeStart, timeEnd):
					print ">>> [REGISTERED] %s %s @ %s | %s - %s" % (idNumber, pinNumber, day, timeStart, timeEnd)
					time = time + 1

					if time > 23:	# 11:00 PM
						# TODO:
						# -	print unused entries
						#
						break;
				else:
					writeData = ">> %s %s" % (idNumber, pinNumber)
					file.write(writeData)

	except Exception as e:
		print e
