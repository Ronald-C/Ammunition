# References:
#	- http://docs.python-requests.org/en/master/api/	

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

HEADERS = { 'User-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36', 
	'Content-Type': 'application/x-www-form-urlencoded', 'Upgrade-Insecure-Requests': 1, 'Referer': 'http://libonline.sjlibrary.org/public/login.aspx', 'Connection':'keep-alive' }
LOGIN_URL = 'http://libonline.sjlibrary.org/public/login.aspx'
SELECTION_URL = 'http://libonline.sjlibrary.org/public/searchoptions.aspx?branchid='

HOURS = ['0000', '0100', '0200', '0300', '0400', '0500', '0600', '0700', '0800', '0900', '1000', '1100', 
	'1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900', '2000', '2100', '2200', '2300']

timeout = 5.0	# Network request timeout
LIBRARY_ROOM = 22	# 22 == MLK Study Room

def login(sessionObj, prev_response, _idNumber, _pinNumber):
	"""
	POST login page payload
	"""
	soup = BeautifulSoup(prev_response.text, 'html.parser')	# Parse response
	
	# Hidden input attributes required for login
	viewState = soup.find('input', attrs={'name': '__VIEWSTATE' }).get('value')
	viewStateGen = soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'}).get('value')
	eventValidation = soup.find('input', attrs={'name': '__EVENTVALIDATION'}).get('value') 

	# Create dictionary payload data
	payload = {'txtCardno': _idNumber, 'txtPIN': _pinNumber, 'btnLogin': 'Sign-in', 'hidPINTextboxVisibleState': 'show',
		'hideCardNoPrefix': '', '__VIEWSTATE': viewState, '__VIEWSTATEGENERATOR': viewStateGen, '__EVENTVALIDATION': eventValidation}

	loginResponse = sessionObj.post(LOGIN_URL, data=payload, headers=HEADERS, timeout=timeout) # data = form-encoded
	if loginResponse.status_code != requests.codes.ok:
		sessionObj.close()	# Close requests.Session
		raise Exception("[NETWORK] %s Client Error" % loginResponse.status_code)

def selectBuilding(sessionOBJ):
	"""
	Given dropdown list, select destination
	"""
	HEADERS['Referer'] = 'http://libonline.sjlibrary.org/public/branchsel.aspx'
	url = SELECTION_URL + str(LIBRARY_ROOM)

	response = sessionOBJ.get(url, headers=HEADERS, cookies=sessionOBJ.cookies, timeout=timeout)
	if response.status_code != requests.codes.ok:
		sessionObj.close()	# Close requests.Session
		raise Exception("[NETWORK] %s Client Error" % response.status_code)

	return BeautifulSoup(response.text, 'html.parser')
	
def attack(_idNumber, _pinNumber, _room_number, _day, _timeStart, _timeEnd):
	"""
	Open request session and access URL
	"""
	with requests.Session() as r:
		# GET initial login landing page
		response = r.get(LOGIN_URL, headers=HEADERS, timeout=timeout)

		################ LOGIN PAGE ################
		login(r, response, _idNumber, _pinNumber)
		
		################ STUDY ROOM SELECTION PAGE ################
		soup = selectBuilding(r)

		################ DATE SELECTION PAGE ################
		viewState = soup.find('input', { 'name': '__VIEWSTATE' }).get('value')
		viewStateGen = soup.find('input', { 'name': '__VIEWSTATEGENERATOR' }).get('value')
		eventValidation = soup.find('input', { 'name': '__EVENTVALIDATION' }).get('value')
		
		# payload = { 'h_ctl00_ContentPlaceHolder1_calSrcDate':'', '__EVENTTARGET':'ctl00$ContentPlaceHolder1$calSrcDate',
		# 	'__EVENTARGUMENT':'', '__LASTFOCUS':'', 'ctl00$hidCardno':soldier,
		# 	'ctl00$hidGoogleMapKey':'ABQIAAAAJKUVL-MrwDN5PN4e9ptZlRT2yXp_ZAY8_ufC3CFXhHIE1NvwkxTptz2NMSRojYVwzZ2DgnujQSVluA',
		# 	'ctl00$hidGoogleMapZoomLevel':'12', 'ctl00$hidGoogleMapLat':'49.244654','ctl00$hidGoogleMapLng':'-122.970657',
		# 	'ctl00$hidEnableGoogeMapScript':'x', 'ctl00$ContentPlaceHolder1$resNextAvail':'rdoResrvNextAvail_No',
		# 	'ctl00$ContentPlaceHolder1$gvPCTypes$ctl01$Item_HeaderLevelCheckBox':'on',
		# 	'ctl00$ContentPlaceHolder1$gvPCTypes$ctl02$Item_RowLevelCheckBox':'on', 'ctl00$ContentPlaceHolder1$ddlApproxStartTime':'',
		# 	'ctl00$ContentPlaceHolder1$ddlNextAvailOrderBy':'StartTime', 'ctl00$ContentPlaceHolder1$ddlMinSlotLengthHour':'0',
		# 	'ctl00$ContentPlaceHolder1$ddlMinSlotLengthMinute':'0', 'ctl00$ContentPlaceHolder1$ddlMaxSlotLengthHour':'0',
		# 	'ctl00$ContentPlaceHolder1$ddlMaxSlotLengthMinute':'0', 'ctl00$ContentPlaceHolder1$ddlNumHoursToSearch':'',
		# 	'ctl00$ContentPlaceHolder1$ddlDisplayResultBy':'pcName', 'ctl00$ContentPlaceHolder1$hidFirstTimeLoad_CheckAllTypes':'0', 
		# 	'__VIEWSTATE': viewState, '__VIEWSTATEGENERATOR':viewStateGen, '__EVENTVALIDATION':eventValidation, '__VIEWSTATEENCRYPTED':'' }

		# client3 = 'http://libonline.sjlibrary.org/public/searchbyMachineTypes.aspx'
		# order3 = s.post(client3, data=payload, headers=HEADERS, cookies=r.cookies)
		# soup3 = BeautifulSoup(order3.text, 'html.parser')



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

		with open(filename, 'rw+') as file:
			
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
					#
					# TODO:
					# - File write not working!!
					#
					writeData = ">> %s %s" % (idNumber, pinNumber)
					file.write(writeData)

			file.close()

	except requests.Timeout as e:
		print "[NETWORK] Request timeout @ %s" % LOGIN_URL
		sys.exit(2)

	except requests.RequestException as e:
		print e
		sys.exit(1)
