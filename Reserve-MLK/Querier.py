from bs4 import BeautifulSoup
import mechanize 	# Me being lazying > requests
import sys

browser = mechanize.Browser()
browser.set_handle_robots(False)

browser.add_handlers = [{ 'User-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36', 
	'Content-Type': 'application/x-www-form-urlencoded', 'Upgrade-Insecure-Requests': 1, 'Referer': 'http://libonline.sjlibrary.org/public/login.aspx', 'Connection':'keep-alive' 
	}]

LOGIN_URL = 'http://libonline.sjlibrary.org/public/login.aspx'
CANCEL_BOOKING_URL = 'http://libonline.sjlibrary.org/public/showCancelBookingSlots.aspx'

def login_account(idNumber, pinNumber):
	browser.select_form(nr=0)
	
	form = browser.form 		# Target form	
	form['txtCardno'] = idNumber
	form['txtPIN'] = pinNumber

	browser.submit()			# Submit form

def isValid(line):
	"""
	Verify the given line is a number
	"""
	return str(line).strip().replace(' ' , '').isdigit()

def verifyBooking(user_id):
	"""
	Verify that there was a booking for King Study Room

	@Return: False if no reservation, else None
	"""
	browser.open(CANCEL_BOOKING_URL)

	if browser.viewing_html():
		soup = BeautifulSoup(browser.response().read(), "html.parser")
		# print soup.prettify()
		tmp = soup.find("td", class_="errortext")
		
		if tmp is not None:		# No Study Room Reserved
			tmp = tmp.next_element.next_element.contents
			
			print ">> %s : %s" % (user_id, tmp[0])
			return False
		
		else:					# Booked rooms found
			target = soup.find("table", id="ctl00_ContentPlaceHolder1_gvbookingInfor")
			rows = target.find_all("tr")
			
			for num in range(1, len(rows)):
				row = rows[num].contents
				
				if str(row[2].string) == "King Study Rooms":
					print user_id

					if room_number is None:
						print ">> %s ... %s ... %s" % (row[4].string[0:8], row[6].string, row[7].string)		
					
					else:
						if row[4].string[5:8] == room_number:
							print ">> %s ... %s" % (row[6].string, row[7].string)
						else:
							print ">> NON-ASSOCIATED ROOM"

	else:
		print "[WARNING] Non-html in %s" % CANCEL_BOOKING_URL

	return None

def query_list(_filename, _room_number=None):
	"""
	This function will loop through filename and init query
	"""

	allValid = True

	try:
		with open(_filename, 'r+') as rFile:
			
			if isinstance(browser, mechanize.Browser):
				browser.open(LOGIN_URL)
				assert browser.viewing_html()		# HTML ???

				for line in rFile:
					validEntry = isValid(line) 		# Confirm that file entry is valid

					try:

						if validEntry:
							_id, _pin = [x for x in line.split()]

							login_account(_id, _pin)		# >> Login

							# Library Online
							browser.select_form(nr=0)		# aspnetForm
							
							responseCode = browser.response().code
							if responseCode is 200:
								
								# If invalid, url does not change
								if LOGIN_URL == browser.geturl():
									allValid = False
									print "[WARNING] Unknown ID: %s" % _id

								else:		# Check for bookings
									if verifyBooking(_id) == False:
										allValid = False 	# no bookings for user found

							else:
								# Possible connection error - terminate
								raise Exception("[ERROR] Status code %s" % responseCode)

						else:
							print "[WARNING] ID/PIN does not meet expected requirements"
						
					except Exception as e:
						print e
						sys.exit(1)

					else:
						browser.open(LOGIN_URL)		# Navigate back to login

			else:
				raise Exception("Not an instance of mechanize.Browser")

		rFile.close()
		if allValid:	
			print "[SUCCESS] All entries are valid!!!"

	except Exception as err:
		print err
		sys.exit(1)
