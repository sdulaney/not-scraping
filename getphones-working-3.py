from bs4 import BeautifulSoup
import urllib
import xlrd, xlwt, xlutils
from xlutils.copy import copy
import time
import re
import requests
import requests_cache

requests_cache.install_cache('thatsthem_cache', backend='sqlite', expire_after=157700000)

# Declare constants (row and column numbers start at 0)
START_ROW = 1                   # cell A2
OWNER_NAME_COL = 13
MAIL_ADDRESS_COL = 0
MAIL_ZIP_COL = 3
FIRST_NAME_COL = 14
LAST_NAME_COL = 15


print 'Phone Number Research Automation', 'Started at ' + time.asctime()

# Grab data from workbook
input_workbook = xlrd.open_workbook("/Users/stewart/Downloads/email-list/propertyfarm.xls")
input_sheet = input_workbook.sheet_by_index(0)
# Copy workbook from xlrd object to xlwt object
write_book = copy(input_workbook)
# Read first sheet
write_sheet = write_book.get_sheet(0)

# Loops through properties in sheet and writes contact info to new excel file
for rownum in range(START_ROW,input_sheet.nrows):

    print '(' + str(rownum) + '/' + str(input_sheet.nrows-1) + ')          ',

    # CorporationWiki Search if LLC
    ownerName = str(input_sheet.cell_value(rownum, OWNER_NAME_COL)).strip()
    ownerName = ownerName.lower()
    if "llc" in ownerName:
        ownerName = ownerName.replace(' ', '%20')
        result = requests.get('https://www.corporationwiki.com/search/results?term=' + ownerName)
        r = result.content
        soup = BeautifulSoup(r)
        myList = []
        for link in soup.find_all('a'):
            # If returns result and result is not another LLC
            if (link.has_attr('data-entity-id') and "llc" not in link.get_text().lower()):
                myList.append(link.get_text())
        if(len(myList) >= 2):
            write_sheet.write(rownum, 9, myList[1])
            print str(input_sheet.cell_value(rownum, OWNER_NAME_COL)).strip() + ' = ' + myList[1],



    # That's Them Reverse Address Search
    mailAddress = str(input_sheet.cell_value(rownum, MAIL_ADDRESS_COL)).strip()
    # Remove consecutive whitespace
    re.sub("\s\s+" , " ", mailAddress)
    # URL encode mail address
    mailAddress = mailAddress.replace(' ', '+')
    zipCode = str(input_sheet.cell_value(rownum, MAIL_ZIP_COL)).strip()
    # Trim long zip codes
    zipCode = zipCode[0:5]
    print input_sheet.cell_value(rownum, MAIL_ADDRESS_COL).strip() + ' ' + zipCode,
    result = requests.get('https://thatsthem.com/advanced-results?d_first=&d_mid=&d_last=&d_email=&d_phone=&d_fulladdr=' + mailAddress + '&d_state=&d_city=&d_zip=' + zipCode)
    if (result.from_cache):
        print '(from cache)'
    r = result.content
    soup = BeautifulSoup(r)
    myList = []
    for link in soup.find_all('a'):
        if("/phone/" in link.get('href')):
            myList.append(link.get('href')[-12:])
    myList = list(set(myList))
    # Grab emails
    fetched_html = result.content
    fetched_emails = []
    emails = fetched_html.split('var p1 = ')
    if(len(emails) > 1):
        for i in range (0, len(emails)):
            if(('var p2 = ') in emails[i] and ('var p3 = ') in emails[i] ):
                email = emails[i].split(';')[0] + emails[i].split('var p2 = ')[1].split(';')[0] + emails[i].split('var p3 = ')[1].split(';')[0];
                fetched_emails.append(email.replace("\"","").replace(" ",""));
                #console.log(email);
        # TODO: search by name, zip code if no emails found


    # That's Them search by name, zip code if above search returns empty
    firstName = str(input_sheet.cell_value(rownum, FIRST_NAME_COL)).strip()
    lastName = str(input_sheet.cell_value(rownum, LAST_NAME_COL)).strip()
    if(firstName != "" and lastName != ""):
        if(len(myList) == 0):
            print('Searching for phones by name, address, zip...')
            result = requests.get('https://thatsthem.com/advanced-results?d_first=' + firstName + '&d_mid=&d_last=' + lastName + '&d_email=&d_phone=&d_fulladdr=&d_state=&d_city=&d_zip=' + zipCode)
            r = result.content
            soup = BeautifulSoup(r)
            for link in soup.find_all('a'):
                if("/phone/" in link.get('href')):
                    myList.append(link.get('href')[-12:])
        if(len(fetched_emails) == 0):
            print('Searching for emails by name, address, zip...')
            result = requests.get('https://thatsthem.com/advanced-results?d_first=' + firstName + '&d_mid=&d_last=' + lastName + '&d_email=&d_phone=&d_fulladdr=&d_state=&d_city=&d_zip=' + zipCode)
            fetched_html = result.content
            fetched_emails = []
            emails = fetched_html.split('var p1 = ')
            if(len(emails) > 1):
                for i in range (0, len(emails)):
                    if(('var p2 = ') in emails[i] and ('var p3 = ') in emails[i] ):
                        email = emails[i].split(';')[0] + emails[i].split('var p2 = ')[1].split(';')[0] + emails[i].split('var p3 = ')[1].split(';')[0];
                        fetched_emails.append(email.replace("\"","").replace(" ",""));

    # Write phone numbers to four columns with additional numbers in a fifth
    print 'Phone: ' + ', '.join(myList)
    additionalList = []
    if(len(myList) > 4):
        additionalList = myList[4:]
        myList = myList[0:4]
        write_sheet.write(rownum, 8, 'Additional Phone Numbers from That\'s Them: ' + ', '.join(additionalList))
    for index in range(len(myList)):
        write_sheet.write(rownum, index+4, myList[index])
    # Write emails to two columns with additional numbers in a third
    print 'Email: ' + ', '.join(fetched_emails)
    additionalEmails = []
    if(len(fetched_emails) > 2):
        additionalEmails = fetched_emails[2:]
        fetched_emails = fetched_emails[0:2]
        write_sheet.write(rownum, 12, 'Additional Emails from That\'s Them: ' + ', '.join(additionalEmails))
    for index in range(len(fetched_emails)):
        write_sheet.write(rownum, index+10, fetched_emails[index])

    # Sleep 0.3s
    time.sleep(0.300)
    # Save spreadsheet every 50 rows
    if((rownum/50) > 1 and rownum%50 == 0):
        write_book.save("/Users/stewart/Downloads/email-list/propertyfarm_processed.xls")
        print 'Saving...'


# ###############################################

# Save the workbook
write_book.save("/Users/stewart/Downloads/email-list/propertyfarm_processed.xls")







# Define apt/pobox string filters
# apt_list = [' apt', ' ste', ' suite', ' apartment', 'po ', 'p.o.', 'po.', 'box']
# Filter out apt/po searches
# if any(str(input_sheet.cell_value(rownum+2, 9)).lower().find(word) != -1 for word in apt_list):
# 	write_sheet.write(rownum+2, 2, "Apartment/PO Box")
