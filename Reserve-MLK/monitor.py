#!/usr/bin/env python

import argparse
import requests
from bs4 import BeautifulSoup
from os import path
from datetime import date, timedelta
import sys
import re

dirPath = path.dirname(path.abspath(__file__))
rootPath = path.join(dirPath, '..') 
sys.path.insert(0, rootPath)		# Include parent dir for global files

from UserAgent import LoadUserAgent


HEADERS = { 'User-agent' : '', 'Content-Type': 'application/x-www-form-urlencoded', 'Upgrade-Insecure-Requests': 1, 
	'Referer': 'http://libonline.sjlibrary.org/public/login.aspx', 'Connection':'keep-alive' }

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
	
def selectDate(soup, sessionObj, _idNumber):
	"""
	GET is sent with date info as package. Return is the response HTML page
	"""
	
	today = date.today()
	# Month and Day does not accept leading 0s
	# startDate;endDate format is expected
 									
	startDate = str(today).replace('-', '.')				# Get today's date

	endDate = today + timedelta(days=5)						# Expected in form-data, today + 5_days
	endDate = str(endDate).replace('-', '.')				# Get date in a week

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

def findRoom(soup, sessionObj, _idNumber, _room_number):
	"""
	Monitor the target of interest by searching for the room in the HTML tables.
	"""

	# Parse the nested tables for the id assoc. with target room
	potentialRooms = soup.findAll('span', id=re.compile('ctl00_ContentPlaceHolder1_gvTimeSlots_ct.+'))
	print potentialRooms


	sys.exit(0)
	
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

def attack(_idNumber, _pinNumber, _room_number):
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
		soup2 = selectDate(soup1, r, _idNumber)

		################ Click <Let Me Choose My Own> ################
		soup3 = selectChooseMyself(soup2, r, _idNumber)

		################ GOTO Computer/Room Time Slots PAGE ################
		soup4 = gotoTables(soup3, r, _idNumber)

		################ BOOK IT!!! ################
		status = findRoom(soup4, r, _idNumber, _room_number)


	return False

def isValid(arg):
	"""
	Verify argument only contains numbers
	"""
	return arg.strip().isdigit()

def main(idNumber, pinNumber, room_number):
	for arg in locals().values():	# Verify digits
		if not isValid(arg):
			raise Exception("Invalid arguments")

	try:
		# Load a random user agent
		HEADERS['User-agent'] = LoadUserAgent()

		if attack(idNumber, pinNumber, room_number):
			
			

	except requests.Timeout as e:
		print "[NETWORK] Request timeout @ %s" % LOGIN_URL
		sys.exit(3)

	except Exception as e:
		print e
		sys.exit(1)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Monitor study room without effort")

	parser.add_argument('ID', help="User's card id")
	parser.add_argument('PIN', help="User's card pin")
	parser.add_argument('Room', help="Room to be monitored")

	if len(sys.argv) > 4:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()
	if args.ID and args.PIN and args.Room:
		# Being monitoring of room using id/pin
		main(args.ID, args.PIN, args.Room)

	else:
		parser.print_help()
		sys.exit(1)