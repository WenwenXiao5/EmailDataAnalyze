# Email Data Analysis ###
This is a data analysis tool which can extract online database, analyze the database, and visualize it.

This program can achieve three major tasks:
1. Extract email archives from a online database and store the data into a sqlite database
2. Run a data-cleaning process to clean up the original sqlite database
3. Output the results in text or use a visualization tool called d3.js.

# Notes ###
- This program utilizes some files from Dr Charles R. Severance's website: https://www.py4e.com/code3/gmane.zip
  The "CocoGmane.py" was wrote by myself, and other files were fully understood and used in this program.
- You need to install the SQLite browser to view and modify the database:
  Refer to https://sqlitebrowser.org/dl/
- The email archive data was pulled dowm from http://mbox.dr-chuck.net/sakai.devel/. This is just a copy of the original gmane database from http://home.gmane.org/.
- Windows has difficulty in displaying UTF-8 characters
  in the console so for each console window you open, you may need
  to type the following command before running this code:

    chcp 65001

  http://stackoverflow.com/questions/388490/unicode-characters-in-windows-command-line-how

# Detailed Process ###
1. Extract email archives from a online database and store the data into a sqlite database
  a) Run CocoGmane.py:
      Mac: python3 CocoGmane.py
      Win: CocoGmane.py
  b) Enter "How many messages: " 
  c) Hit "Return" to jump out of the command
  
  The base url "http://mbox.dr-chuck.net/sakai.devel/" is hard coded in the spidering process. You can spider another repository by changing that base url.   Make sure to delete the content.sqlite file if you switch the base url.
  
  CocoGmane is a spider that retrieves mail messages to content.sqlite. This is a restartable process which can pick up from where it's left off.

  It may take long to retrieve all the mail messages. Therefore, you can also download the pre-spidered content.sqlite database from https://www.py4e.com/data_space/content.sqlite.zip to proceed to next step.
   
  The content.sqlite data is pretty raw, with an innefficient data model, and not compressed.
This is intentional as it allows you to look at content.sqlite to debug the process.
  
2. Run a data-cleaning process to clean up the original content.sqlite database and obtain a cleaned-up index.sqlite database
   a) Run gmodel.py:
      Mac: python3 gmodel.py 
      Win: gmodel.py

      Each time gmodel.py runs - it completely wipes out and re-builds index.sqlite.
      
      The file index.sqlite will be much smaller (often 10X smaller) than content.sqlite because it also compresses the header and body text.

 The gmodel.py program does a number of data cleaing steps: 

    Domain names are truncated to two levels for .com, .org, .edu, and .net 
    other domain names are truncated to three levels.  So si.umich.edu becomes
    umich.edu and caret.cam.ac.uk becomes cam.ac.uk.   Also mail addresses are
    forced to lower case and some of the @gmane.org address like the following

       arwhyte-63aXycvo3TyHXe+LvDLADg@public.gmane.org

    are converted to the real address whenever there is a matching real email
    address elsewhere in the message corpus.

    If you look in the content.sqlite database there are two tables that allow
    you to map both domain names and individual email addresses that change over 
    the lifetime of the email list.  For example, Steve Githens used the following
    email addresses over the life of the Sakai developer list:

    s-githens@northwestern.edu
    sgithens@cam.ac.uk
    swgithen@mtu.edu

    We can add two entries to the Mapping table

    s-githens@northwestern.edu ->  swgithen@mtu.edu
    sgithens@cam.ac.uk -> swgithen@mtu.edu

    And so all the mail messages will be collected under one sender even if 
    they used several email addresses over the lifetime of the mailing list.

    You can also make similar entries in the DNSMapping table if there are multiple
    DNS names you want mapped to a single DNS.  In the Sakai data I add the following
    mapping:

    iupui.edu -> indiana.edu

    So all the folks from the various Indiana University campuses are tracked together

    You can re-run the gmodel.py over and over as you look at the data, and add mappings
    to make the data cleaner and cleaner. 


3. Output the results in text or use a visualization tool called d3.js.
  a) If you want to do just the simplest data analysis of "who does the most" and "which 
organzation does the most":
    run gbasic.py as follows:

    Mac: python3 gbasic.py
    Win: gbasic.py

    This shows the top email list participants, and the top email list organizations

  b) If you want to visualize the word frequence in the subject lines: 
    run gword.py:

    Mac: python3 gword.py:
    Win: gword.py:

    This produces the file gword.js which you can visualize using the file 
gword.htm.

  c) If you want to visualize the email participation by organizations over time:
    run gline.py:

    Mac: python3 gline.py:
    Win: gline.py:
    
    Its output is written to gline.js which is visualized using gline.htm.
