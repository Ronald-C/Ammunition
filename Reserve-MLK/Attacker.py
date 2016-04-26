# References:
#	- http://docs.python-requests.org/en/master/api/	

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
import sys

HEADERS = { 'User-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36', 
	'Content-Type': 'application/x-www-form-urlencoded', 'Upgrade-Insecure-Requests': 1, 'Referer': 'http://libonline.sjlibrary.org/public/login.aspx', 'Connection':'keep-alive' }

HOURS = ['0000', '0100', '0200', '0300', '0400', '0500', '0600', '0700', '0800', '0900', '1000', '1100', 
	'1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900', '2000', '2100', '2200', '2300']

LOGIN_URL = 'http://libonline.sjlibrary.org/public/login.aspx'
BRANCH_URL = 'http://libonline.sjlibrary.org/public/searchoptions.aspx?branchid='
SELECT_TYPE_URL = 'http://libonline.sjlibrary.org/public/searchbyMachineTypes.aspx'
TIME_SLOTS_URL = 'http://libonline.sjlibrary.org/public/searchByMTListing.aspx'

timeout = 5.0	# Network request timeout
LIBRARY_ROOM = 22	# 22 == MLK Study Room

def login(sessionObj, prev_response, _idNumber, _pinNumber):
	"""
	Argument 'prev_response' is the login_page response.
	Function will POST payload data (hidden variables) to login_page url
	and return a response that is parsed with BeautifulSoup
	"""
	soup = BeautifulSoup(prev_response.text, 'html.parser')	# Parse response
	
	# Hidden input attributes required for login
	viewState = soup.find('input', attrs={ 'name': '__VIEWSTATE' }).get('value')
	viewStateGen = soup.find('input', attrs={ 'name': '__VIEWSTATEGENERATOR' }).get('value')
	eventValidation = soup.find('input', attrs={ 'name': '__EVENTVALIDATION' }).get('value') 

	# Create dictionary payload data
	payload = {'txtCardno': _idNumber, 'txtPIN': _pinNumber, 'btnLogin': 'Sign-in', 'hidPINTextboxVisibleState': 'show',
		'hideCardNoPrefix': '', '__VIEWSTATE': viewState, '__VIEWSTATEGENERATOR': viewStateGen, '__EVENTVALIDATION': eventValidation
		}

	loginResponse = sessionObj.post(LOGIN_URL, data=payload, headers=HEADERS, timeout=timeout) # data = form-encoded
	if loginResponse.status_code != requests.codes.ok:			# ERROR if not 200 response
		raise Exception("[NETWORK] %s Client Error" % loginResponse.status_code)

def selectBuilding(sessionOBJ):
	"""
	Currently on selection page. Function will select the building of interest
	defined by variable 'LIBRARY_ROOM' from the dropdown menu
	"""
	HEADERS['Referer'] = 'http://libonline.sjlibrary.org/public/branchsel.aspx'
	url = BRANCH_URL + str(LIBRARY_ROOM)

	response = sessionOBJ.get(url, headers=HEADERS, cookies=sessionOBJ.cookies, timeout=timeout)
	if response.status_code != requests.codes.ok:			# ERROR if not 200 response
		raise Exception("[NETWORK] %s Client Error" % response.status_code)

	return BeautifulSoup(response.text, 'html.parser')
	
def selectDate(soup, sessionObj, _idNumber, _day):
	"""
	Still on selection page. Function manipulates '_day' to acceptable format 
	and verify date is within a valid range. LIMIT: 5-day from present date
	"""
	today = date.today()
	# Month and Day does not accept leading 0s
	# startDate;endDate format is expected

	startDate = today - timedelta(days=today.weekday())		# today - day_of_the_week
	startDate = str(startDate).replace('-', '.')			# Get beginning of week (Monday)

	endDate = today + timedelta(days=6)						# today + 6_days
	endDate = str(endDate).replace('-', '.')				# Get date in a week

	if ( int(startDate.replace('.', '')) > int(_day) ) or ( int(_day) > int(endDate.replace('.', '')) ):
		raise Exception("[PARAMETER] Day specified out of range")
	
	else:
		startDate = startDate[:5] + startDate[5:].replace('0', '')			# Remove leading 0s
		
		endDate = endDate[:6] + str(int(endDate[6]) - 1) + endDate[7:]		# endDate = Month - 1
		endDate = endDate[:5] + endDate[5:].replace('0', '')				# Remove leading 0s

		targetDate = startDate + ';' + endDate

	# Gather hidden variables for reservation selection
	viewState = soup.find('input', attrs={ 'name': '__VIEWSTATE' }).get('value')
	viewStateGen = soup.find('input', attrs={ 'name': '__VIEWSTATEGENERATOR' }).get('value')
	eventValidation = soup.find('input', attrs={ 'name': '__EVENTVALIDATION' }).get('value')

	payload = {'h_ctl00_ContentPlaceHolder1_calSrcDate': targetDate, '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$calSrcDate', '__EVENTARGUMENT': '','__LASTFOCUS': '',
		'ctl00$hidCardno': _idNumber, 'ctl00$hidGoogleMapKey': 'ABQIAAAAJKUVL-MrwDN5PN4e9ptZlRT2yXp_ZAY8_ufC3CFXhHIE1NvwkxTptz2NMSRojYVwzZ2DgnujQSVluA',
		'ctl00$hidGoogleMapZoomLevel': '12', 'ctl00$hidGoogleMapLat': '49.244654', 'ctl00$hidGoogleMapLng': '-122.970657', 'ctl00$hidEnableGoogeMapScript': 'x',
		'ctl00$ContentPlaceHolder1$resNextAvail': 'rdoResrvNextAvail_No', 'ctl00$ContentPlaceHolder1$gvPCTypes$ctl01$Item_HeaderLevelCheckBox': 'on',
		'ctl00$ContentPlaceHolder1$gvPCTypes$ctl02$Item_RowLevelCheckBox': 'on', 'ctl00$ContentPlaceHolder1$ddlApproxStartTime': '', 
		'ctl00$ContentPlaceHolder1$ddlNextAvailOrderBy': 'StartTime', 'ctl00$ContentPlaceHolder1$ddlMinSlotLengthHour': '0', 
		'ctl00$ContentPlaceHolder1$ddlMinSlotLengthMinute': '0', 'ctl00$ContentPlaceHolder1$ddlMaxSlotLengthHour': '0', 
		'ctl00$ContentPlaceHolder1$ddlMaxSlotLengthMinute': '0', 'ctl00$ContentPlaceHolder1$ddlNumHoursToSearch': '', 
		'ctl00$ContentPlaceHolder1$ddlDisplayResultBy': 'pcName', 'ctl00$ContentPlaceHolder1$hidFirstTimeLoad_CheckAllTypes': '0', 
		'__VIEWSTATE': viewState, '__VIEWSTATEGENERATOR': viewStateGen, '__EVENTVALIDATION': eventValidation, '__VIEWSTATEENCRYPTED': '' 
		}

	response = sessionObj.post(SELECT_TYPE_URL, data=payload, headers=HEADERS, cookies=sessionObj.cookies)
	if response.status_code != requests.codes.ok:			# ERROR if not 200 response
		raise Exception("[NETWORK] %s Client Error" % response.status_code)

	return BeautifulSoup(response.text, 'html.parser')

def selectChooseMyself(soup, sessionObj, _idNumber):
	"""
	Still on selection page. Function selects HTML 
	radio button <Let Me Choose Myself>.
	"""
	# Gather hidden variables for reservation selection
	viewState = soup.find('input', attrs={ 'name': '__VIEWSTATE' }).get('value')
	viewStateGen = soup.find('input', attrs={ 'name': '__VIEWSTATEGENERATOR' }).get('value')
	eventValidation = soup.find('input', attrs={ 'name': '__EVENTVALIDATION' }).get('value')

	package = {'h_ctl00_ContentPlaceHolder1_calSrcDate': '', '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$rdoResrvNextAvail_No', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': viewState,
		'__VIEWSTATEGENERATOR': viewStateGen, '__VIEWSTATEENCRYPTED': '', '__EVENTVALIDATION': eventValidation, 'ctl00$hidCardno': _idNumber, 'ctl00$hidGoogleMapKey': 'ABQIAAAAJKUVL-MrwDN5PN4e9ptZlRT2yXp_ZAY8_ufC3CFXhHIE1NvwkxTptz2NMSRojYVwzZ2DgnujQSVluA',
		'ctl00$hidGoogleMapZoomLevel': '12', 'ctl00$hidGoogleMapLat': '49.244654', 'ctl00$hidGoogleMapLng': '-122.970657', 'ctl00$hidEnableGoogeMapScript': 'x',
		'ctl00$ContentPlaceHolder1$resNextAvail': 'rdoResrvNextAvail_No', 'ctl00$ContentPlaceHolder1$gvPCTypes$ctl01$Item_HeaderLevelCheckBox': 'on',
		'ctl00$ContentPlaceHolder1$gvPCTypes$ctl02$Item_RowLevelCheckBox': 'on', 'ctl00$ContentPlaceHolder1$ddlApproxStartTime': '', 'ctl00$ContentPlaceHolder1$ddlNextAvailOrderBy': 'StartTime',
		'ctl00$ContentPlaceHolder1$ddlMinSlotLengthHour': '0', 'ctl00$ContentPlaceHolder1$ddlMinSlotLengthMinute': '0', 'ctl00$ContentPlaceHolder1$ddlMaxSlotLengthHour': '0',
		'ctl00$ContentPlaceHolder1$ddlMaxSlotLengthMinute': '0', 'ctl00$ContentPlaceHolder1$ddlNumHoursToSearch': '', 'ctl00$ContentPlaceHolder1$ddlDisplayResultBy': 'pcName',
		'ctl00$ContentPlaceHolder1$hidFirstTimeLoad_CheckAllTypes': '0'
	}

	response = sessionObj.get(SELECT_TYPE_URL, data=package, headers=HEADERS, cookies=sessionObj.cookies)
	if response.status_code != requests.codes.ok:			# ERROR if not 200 response
		raise Exception("[NETWORK] %s Client Error" % response.status_code)

	return BeautifulSoup(response.text, 'html.parser')

def gotoTables(soup, sessionObj, _idNumber):
	viewState = soup.find('input', attrs={ 'name': '__VIEWSTATE' }).get('value')
	viewStateGen = soup.find('input', attrs={ 'name': '__VIEWSTATEGENERATOR' }).get('value')
	eventValidation = soup.find('input', attrs={ 'name': '__EVENTVALIDATION' }).get('value')

	package = { 'h_ctl00_ContentPlaceHolder1_calSrcDate': '' ,'__EVENTTARGET':'','__EVENTARGUMENT': '', '__LASTFOCUS': '', 'ctl00$hidCardno': _idNumber,
		'ctl00$hidGoogleMapKey': 'ABQIAAAAJKUVL-MrwDN5PN4e9ptZlRT2yXp_ZAY8_ufC3CFXhHIE1NvwkxTptz2NMSRojYVwzZ2DgnujQSVluA', 'ctl00$hidGoogleMapZoomLevel': '12',
		'ctl00$hidGoogleMapLat': '49.244654', 'ctl00$hidGoogleMapLng': '-122.970657', 'ctl00$hidEnableGoogeMapScript': 'x', 'ctl00$ContentPlaceHolder1$resNextAvail': 'rdoResrvNextAvail_No',
		'ctl00$ContentPlaceHolder1$gvPCTypes$ctl01$Item_HeaderLevelCheckBox': 'on', 'ctl00$ContentPlaceHolder1$gvPCTypes$ctl02$Item_RowLevelCheckBox': 'on', 'ctl00$ContentPlaceHolder1$ddlApproxStartTime': '',
		'ctl00$ContentPlaceHolder1$ddlNextAvailOrderBy': 'StartTime', 'ctl00$ContentPlaceHolder1$ddlMinSlotLengthHour': '0', 'ctl00$ContentPlaceHolder1$ddlMinSlotLengthMinute': '0',
		'ctl00$ContentPlaceHolder1$ddlMaxSlotLengthHour': '0', 'ctl00$ContentPlaceHolder1$ddlMaxSlotLengthMinute': '0', 'ctl00$ContentPlaceHolder1$ddlNumHoursToSearch': '',
		'ctl00$ContentPlaceHolder1$ddlDisplayResultBy': 'pcName', 'ctl00$ContentPlaceHolder1$btnSearch': '+++Schedule+Now+++', 'ctl00$ContentPlaceHolder1$hidFirstTimeLoad_CheckAllTypes': '0',
		'__VIEWSTATE': viewState, '__VIEWSTATEGENERATOR': viewStateGen, '__EVENTVALIDATION': eventValidation, '__VIEWSTATEENCRYPTED': '' }

	response = sessionObj.post(SELECT_TYPE_URL, data=package, headers=HEADERS, cookies=sessionObj.cookies)
	if response.status_code != requests.codes.ok:				# ERROR if not 200 response
		raise Exception("[NETWORK] %s Client Error" % response.status_code)

	return BeautifulSoup(response.text, 'html.parser')

def attack(_idNumber, _pinNumber, _room_number, _day, _timeStart, _timeEnd):
	"""
	Open request session and access URL
	"""
	with requests.Session() as r:
		response = r.get(LOGIN_URL, headers=HEADERS, timeout=timeout)	# GET initial login landing page

		################ SUBMIT LOGIN PAGE ################
		login(r, response, _idNumber, _pinNumber)
		################ STUDY ROOM SELECTION PAGE ################
		soup1 = selectBuilding(r)
		################ DATE SELECTION PAGE ################
		soup2 = selectDate(soup1, r, _idNumber, _day)
		################ Click <Let Me Choose My Own> ################
		soup3 = selectChooseMyself(soup2, r, _idNumber)
		################ GOTO Computer/Room Time Slots PAGE ################
		soup4 = gotoTables(soup3, r, _idNumber)
		

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
	day_formatted = str(datetime.strptime(day, '%Y%m%d')).split()[0]
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
					print ">>> [REGISTERED] %s %s @ %s | %s - %s" % (idNumber, pinNumber, day_formatted, timeStart, timeEnd)
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
