import ssl
import sqlite3
import urllib.request
import re
import time

# Not all systems have this so conditionally define parser
try:
    from dateutil.parser import parse
except:
    print('You need to install dateutil using command: pip install python-dateutil')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get tje url of Gmane list
url = input('Whats the Gmane url: ')
if len(url) < 1:
    url = "http://mbox.dr-chuck.net/sakai.devel/"

# Create database content.sqlite
conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Messages
            (id INTEGER UNIQUE, email TEXT, sent_at TEXT,
            subject TEXT, headers TEXT, body TEXT)''')

# Find out where we left off
cur.execute('SELECT max(id) FROM Messages')
try:
    num = cur.fetchone()
    # print (num)
    if num is None:
        start = 0
    else:
        start = num[0]
except:
    start = 0

# If we are starting from an empty database, num is a tuple: (None,)
if start is None: 
    start = 0 

# We are only allowed to fail 5 times per page
# Conditions of fails: 
# Cannot retrieve the full url; Does not start with From; 
# Cannot find the break between header and body; Cannot parse the sent_to date
fail = 0
count = 0
number = 0
while True:
    if count < 1:
        page = input('How many messages: ')
        if len(page) < 1:
            break
        count = int(page)

    # Double check if we start from previously where we left off:
    start = start + 1
    cur.execute('SELECT id FROM Messages WHERE id = ?', (start,))
    try:
        num = cur.fetchone()
        if num is not None:
            continue
    except:
        num = None
    
    count = count -1

    # Continue using the full url:
    fullurl = url + str(start) + '/' + str(start + 1)

    try:
        doc = urllib.request.urlopen(fullurl, None, 30, context=ctx)
        text = doc.read().decode()
        if doc.getcode() != 200:
            print('Error code: ', doc.getcode(), 'of the url: ', fullurl)
            break
    except KeyboardInterrupt:
        print('Program interrupted by user...')
    except Exception as Ex:
        print('Unable to retrieve the fullurl', fullurl)
        print('Due to error: ', Ex)
        fail = fail + 1
        if fail > 5:
            break
        continue
    
    # Print out the url and number of characters in text
    print(fullurl, len(text))

    # Count on the number of pages/url that have been retrieved
    number = number + 1

    # Retrieve information from the text:
    # Check if the format of text is correct:
    if not text.startswith('From'):
        print('It does not start with From')
        fail = fail + 1
        if fail > 5:
            break
        continue # If not, this page is not worth retrieving info, 
    # go to next page

    # Find header and body part:
    ind = text.find('\n\n')
    if ind > 0:
        header = text[:ind]
        body = text[(ind+2):]
    else: 
        print('Cannot find the break between header and body')
        fail = fail + 1
        if fail > 5:
            break
        continue

    # Find email
    ee = re.findall('\nFrom: .* <(\S+@\S+)>\n', header)
    if len(ee) == 1:
        email = ee[0]
        email = email.lower().strip()
        email = email.replace("<","")
    
    else:
        ee = re.findall('\nFrom: (\S+@\S+)\n', header)
        if len(ee) == 1:
            email = ee[0]
            email = email.lower().strip()
            email = email.replace("<","")

    # Find sent_at date
    dd = re.findall('\nDate: .*, (.*)\n', header)
    if len(dd) == 1:
        date = dd[0]
        date = date[:26] # hard counted to be the first 26 characters
        # Try to parse the date using 
        try:
            sent_at = parse(date)
        except:
            print('Cannot parse: ', date)
            fail = fail + 1
            if fail > 5:
                break
            continue

    # Find subject
    hh = re.findall('\nSubject: (.*)\n', header)
    if len(hh) == 1:
        subject = hh[0]
        subject = subject.lower().strip()

    # Reset fail counter:
    fail = 0

    # Print the information retrieved:
    print('     ', email, sent_at, subject)

    # Store these info to database:
    cur.execute('''INSERT OR IGNORE INTO Messages 
                (id, email, sent_at, subject, headers, body)
                VALUES (?, ?, ?, ?, ?, ?)''', (start, email, sent_at, subject, header, body))
    if number %50 == 0:
        conn.commit() # Commit every 50 urls
    if number %100 == 0:
        time.sleep(1) # Pause the program for 1 sec every 100 urls

conn.commit()
cur.close()

