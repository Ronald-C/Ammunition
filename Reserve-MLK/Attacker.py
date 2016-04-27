# References:
#	- http://docs.python-requests.org/en/master/api/	

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
import sys
import re

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
	Argument 'prev_response' is the HTML login_page response. Function will POST 
	payload data (hidden variables) and login credentials to login_page url
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
		raise Exception("[NETWORK] %s Client Error - Login" % loginResponse.status_code)

def selectBuilding(sessionOBJ):
	"""
	GET selection page. Payload will contain the building of interest defined by 
	variable 'LIBRARY_ROOM' from the dropdown menu. Return is the response HTML page
	"""
	
	HEADERS['Referer'] = 'http://libonline.sjlibrary.org/public/branchsel.aspx'
	url = BRANCH_URL + str(LIBRARY_ROOM)

	response = sessionOBJ.get(url, headers=HEADERS, cookies=sessionOBJ.cookies, timeout=timeout)
	if response.status_code != requests.codes.ok:			# ERROR if not 200 response
		raise Exception("[NETWORK] %s Client Error - Building selection" % response.status_code)


	if response.url == 'http://libonline.sjlibrary.org/public/login.aspx?SelectedLanguage=&msgToDisplay=Your+session+is+no+longer+valid.++Please+login+again.&FromPage=':
		return False

	return BeautifulSoup(response.text, 'html.parser')
	
def selectDate(soup, sessionObj, _idNumber, _day):
	"""
	Still on selection page. Function manipulates '_day' to acceptable format 
	and verify date is within a valid range; a GET is sent with this info as package
	Return is the response HTML page
	"""
	
	today = date.today()
	# Month and Day does not accept leading 0s
	# startDate;endDate format is expected
 									
	startDate = str(today).replace('-', '.')				# Get beginning of week (Monday)

	endDate = today + timedelta(days=5)						# Expected in form-data, today + 5_days
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

	payload = {'h_ctl00_ContentPlaceHolder1_calSrcDate': targetDate, '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$calSrcDate', '__EVENTARGUMENT': '', '__LASTFOCUS': '',
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

	HEADERS['Referer'] = SELECT_TYPE_URL 	# Where we are from

	response = sessionObj.post(SELECT_TYPE_URL, data=payload, headers=HEADERS, cookies=sessionObj.cookies)
	if response.status_code != requests.codes.ok:			# ERROR if not 200 response
		raise Exception("[NETWORK] %s Client Error - Date selection" % response.status_code)

	return BeautifulSoup(response.text, 'html.parser')

def selectChooseMyself(soup, sessionObj, _idNumber):
	"""
	Still on selection page. Function selects HTML radio button <Let Me Choose Myself>. 
	This is a GET to the same URL, with this data as payload. Return is the response HTML page
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
		raise Exception("[NETWORK] %s Client Error - Radio button selection" % response.status_code)

	return BeautifulSoup(response.text, 'html.parser')

def gotoTables(soup, sessionObj, _idNumber):
	"""
	All parameters were sent. GET the time-tables that indicate free slots.
	Return is the response HTML page, which is the tables.
	"""

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
		raise Exception("[NETWORK] %s Client Error - GOTO tables" % response.status_code)

	return BeautifulSoup(response.text, 'html.parser')

def bookRoom(soup, sessionObj, _idNumber, _room_number, _timeStart, _timeEnd):
	"""
	Book the target of interest by searching for the room+time in the HTML tables. A success
	is a returned 200 status code. If room+time not found, exception is raised - terminate script. 
	"""

	timeA = datetime.strptime( _timeStart[:2] + ':' + _timeStart[2:], '%H:%M' ).strftime('%I:%M %p') 
	timeB = datetime.strptime( _timeEnd[:2] + ':' + _timeEnd[2:], '%H:%M' ).strftime('%I:%M %p')
	if timeA[0] == '0':
		timeA = timeA[1:]		# Remove leading 0
	if timeB[0] == '0':
		timeB = timeB[1:]

	targetRoom = timeA + ' - ' + timeB 		# Format start-end time
	ROOM_TAG = None

	# Parse the nested tables for the id assoc. with target room
	potentialRooms = soup.findAll('span', id=re.compile('ctl00_ContentPlaceHolder1_gvTimeSlots_ct.+'))
	for room in potentialRooms:

		if str(room.string)[:8] == "Room " + _room_number:
			timeSlots = room.parent.nextSibling.tr

			for time in timeSlots:		# Find the <tr> (room) tag of interest
				if time.string.encode('utf-8') == targetRoom:
					
					ROOM_TAG = str(time.a.get('id') )			# Each room has a unique ROOM_TAG
					break;
	
	# If room not found; does not exist or already reserved
	if ROOM_TAG == None:	
		raise Exception("[ERROR] Room %s @ %s Not Found" % (_room_number, targetRoom))

	# Find the hidden variables required in request
	viewState = soup.find('input', { 'name': '__VIEWSTATE' }).get('value')
	viewStateGen = soup.find('input', { 'name': '__VIEWSTATEGENERATOR' }).get('value')
	eventValidation = soup.find('input', { 'name': '__EVENTVALIDATION' }).get('value')

	index = ROOM_TAG.rfind('LnkBtn_') + len('LnkBtn_')
	clickedLinkButtonValue = ROOM_TAG[index:]
	
	__EVENTTARGET = ROOM_TAG.replace('_', '$', 2)

	package = {'__EVENTTARGET': __EVENTTARGET, '__EVENTARGUMENT': '', 'ctl00$hidCardno': _idNumber,
		'ctl00$hidGoogleMapKey': 'ABQIAAAAJKUVL-MrwDN5PN4e9ptZlRT2yXp_ZAY8_ufC3CFXhHIE1NvwkxTptz2NMSRojYVwzZ2DgnujQSVluA', 'ctl00$hidGoogleMapZoomLevel': '12',
		'ctl00$hidGoogleMapLat': '49.244654', 'ctl00$hidGoogleMapLng': '-122.970657', 'ctl00$hidEnableGoogeMapScript': 'x', 
		'ctl00$ContentPlaceHolder1$hidClickedLinkButtonValue': clickedLinkButtonValue, 'ctl00$ContentPlaceHolder1$hid_PoolMachineDisplayName': 'To be determined', 
		'__VIEWSTATE': viewState, '__VIEWSTATEGENERATOR': viewStateGen, '__EVENTVALIDATION': eventValidation 
		}

	response = sessionObj.post(TIME_SLOTS_URL, data=package, headers=HEADERS, cookies=sessionObj.cookies)
	receipt = BeautifulSoup(response.text, 'html.parser')

	if response.status_code == requests.codes.ok:
		return True

	return False	

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
		if soup1 == False:	# Was not able to login
			return False

		################ SELECT TARGET DATE ################
		soup2 = selectDate(soup1, r, _idNumber, _day)

		################ Click <Let Me Choose My Own> ################
		soup3 = selectChooseMyself(soup2, r, _idNumber)

		################ GOTO Computer/Room Time Slots PAGE ################
		soup4 = gotoTables(soup3, r, _idNumber)

		################ BOOK IT!!! ################
		status = bookRoom(soup4, r, _idNumber, _room_number, _timeStart, _timeEnd)

		return status

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
	
	### Validate military format. If 24:00, this is equivalent to 00:00 or index 0 
	### If format is invalid, terminate execution of program
	
	if time == 24:		# 24 == Midnight (00:00)
		time = 0

	if time < 0 or time > 23:		# Verify time format
		print 'Time must be between 0 and 23 (inclusive)'
		sys.exit(2)	

	if len(day) != 8:				# Verify day format
		print 'Argument day (-d) must be in yyyymmdd format'
		sys.exit(2)

	try:
		### Open the file and loop entries; first validate them. Some start/end times are weird (not full hour).  
		### If successful reservation, and not last reservation, increment time for next user in file. If not 
		### successful, this means id/pin was invalid - log this information to file and stdout

		with open(filename, 'rw+') as file:	
			for line in nonblank_lines(file):

				idNumber, pinNumber = [ entry for entry in line.split() ]
				timeStart = HOURS[time]

				if timeStart == '2300':		# If 11:00PM (23:00), timeEnd == 11:55PM (23:55)
					timeEnd = '2355'

				elif timeStart == '0000':	# If Midnight (00:00). timeEnd == 12:55AM (00:55)
					timeEnd = '0055'

				else:
					timeEnd = HOURS[time + 1]

				# Register user
				if attack(idNumber, pinNumber, room_number, day, timeStart, timeEnd):
					print ">>> [REGISTERED] %s %s @ %s | %s - %s" % (idNumber, pinNumber, day_formatted, timeStart, timeEnd)
	
					# Just reserved 12:00 - 12:55. Terminate execution 
					if time == 0:	
						print "End of study hours encountered. Terminating . . ."
						break;
					
					else:
						# Continue reserving room
						time = time + 1
				
				else:
					print "[WARNING] %s is invalid " % idNumber
					# Unable to log in
					# TODO:
					#	- Overwrite file entries; log it

			file.close()

	except requests.Timeout as e:
		print "[NETWORK] Request timeout @ %s" % LOGIN_URL
		sys.exit(2)

	except Exception as e:
		print e
		sys.exit(1)
