# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup

#### FUNCTIONS 1.0

def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url):
    try:
        r = urllib2.urlopen(url)
        count = 1
        while r.getcode() == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = urllib2.urlopen(url)
        sourceFilename = r.headers.get('Content-Disposition')

        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.getcode() == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx', '.pdf']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False


def validate(filename, file_url):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string

#### VARIABLES 1.0

entity_id = "FTRJZX_KCHNHSFT_gov"
url = "https://www.kch.nhs.uk/about/corporate/foi/publication-scheme/trust-spend"
errors = 0
data = []


#### READ HTML 1.0

html = urllib2.urlopen(url)
soup = BeautifulSoup(html, 'lxml')

#### SCRAPE DATA

links = soup.find('ul', 'showMoreList bullet').find_all('a', 'download file')
for link in links:
            url = link['href']
            try:
                title = link.text.strip()
            except:
                pass
            if not title:
                continue
            csvMth = csvYr = ''
            if 'Month 1' in title:
                csvMth = '04'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'Month 2' in title:
                csvMth = '05'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'Month 3' in title:
                csvMth = '06'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'Month 4' in title:
                csvMth = '07'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'Month 5' in title:
                csvMth = '08'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'Month 6' in title:
                csvMth = '09'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'Month 7' in title:
                csvMth = '10'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'Month 8' in title:
                csvMth = '11'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'Month 9' in title:
                csvMth = '12'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'onth' not in title:
                csvMth = 'Y1'
                csvYr = title.split('-')[0].strip()[-4:]
            elif 'First six months':
                csvMth = 'Q0'
                csvYr = title.split('-')[0].strip()[-4:]
            if u'10' in title.split()[-1]:
                csvMth = '01'
                csvYr = title.split('-')[1].strip()[:4]
            elif re.findall('\\bMonth 11\\b', title):
                csvMth = '02'
                csvYr = title.split('-')[1].strip()[:4]
            elif re.findall('\\bMonth 12\\b', title):
                csvMth = '03'
                csvYr = title.split('-')[1].strip()[:4]
            # print csvYr, csvMth
            csvMth = convert_mth_strings(csvMth.upper())
            data.append([csvYr, csvMth, url])



#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF
