#!/usr/bin/python3

#apt-get update
#apt-get dist-upgrade
#apt-get install python3-pip
#pip3 install selenium
#apt-get install chromium-chromedriver
#apt install xvfb

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium import webdriver
from urllib.error import HTTPError
from urllib.error import ContentTooShortError
import time
import random
import re
import json
import sys
import hashlib
import urllib.request
import os
import socket

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('log-level=3')
#chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)

waitMin=5
waitMax=10
wordDB_file="wordDB_file"
linksDB_file="linksDB_file"
historyDB_file="historyDB_file"
initialURL="https://siteaddress.com/"
specialChars='().,[]{}"&:#-=?!\'/\\´%$@^*|;><~`_+'
specialCharsFN='@#%?*:"*/<>\|`'
wordDB={'misfits'}
linksDB={''}
historyDB={''}
songsFolder="downloads/"

def downloadSong(url,name,linksDB):
    directory=hashlib.md5(name.encode()).hexdigest()[0:2]
    dirExists = os.path.exists(songsFolder+directory)
    if not dirExists:
        os.makedirs(songsFolder+directory)
    fileName=songsFolder+directory+"/"+name.translate({ord(x): '' for x in specialCharsFN})[:240]+".mp3"
    print('Downloading {}/{}'.format(directory,name))
    retries=3
    while retries > 0 :
        try:
            urllib.request.urlretrieve(url,fileName)
            break
        except HTTPError as err:
            print("Error: %s, reason: %s. Retrying (%i).." % (err.code, err.reason, retries))
            retries=retries-1
        except IOError as err:
            print("Error: %s, reason: %s. Retrying (%i).." % (err.errno, err.strerror, retries))
            retries=retries-1
        except socket.timeout as err:
            print("Network error: %s. Retrying (%i).." % (err.strerror, retries))
            retries=retries-1
        except socket.error as err:
            print("Network error: %s. Retrying (%i).." % (err.strerror, retries))
            retries=retries-1
        except ContentTooShortError as err:
            print("Error: The downloaded data is less than the expected amount. Skipping.")
            retries=retries-1
    if retries <= 0:
        return False
    linksDB.add(name)
    saveLinksDB()
    return True

def extractAllLinks(browser,linksDB,wordDB):
    for panel in browser.find_elements(by=By.ID, value='liveaudio'):
        if panel.text == "something went wrong..":
            return False
        else:
            for link in panel.find_elements(by=By.PARTIAL_LINK_TEXT, value=''):
                eurl=link.get_attribute("href")
                ltext=link.text
                if ltext != '':
                    if link.text not in linksDB:
                        includeName(link.text,wordDB)
                        downloadSong(eurl,link.text,linksDB)
                        time.sleep(random.randint(waitMin,waitMax))
                    else:
                        print("Already downloaded {}".format(link.text))
            return True
    return True

def includeName(name,wordDB):
    name = name.translate({ord(x): ' ' for x in specialChars})
    name = name.lower()
    wordDB.update(re.split(" +",name))
    wordDB.discard('')
    saveWordDB()

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
        raise TypeError

def saveWordDB():
    with open(wordDB_file, 'w') as outfile:
        result=json.dumps(wordDB,default=set_default)
        outfile.write(result)

def saveHistoryDB():
    with open(historyDB_file, 'w') as outfile:
        result=json.dumps(historyDB,default=set_default)
        outfile.write(result)

def saveLinksDB():
    with open(linksDB_file, 'w') as outfile:
        result=json.dumps(linksDB,default=set_default)
        outfile.write(result)

def loadWordDB():
    try:
        f = open(wordDB_file,)
        wordDB = set(json.load(f))
        f.close()
    except FileNotFoundError as e:
        print("File not found. Using initial word/wordlist as database.")
        return {}
    return wordDB

def loadHistoryDB():
    try:
        f = open(historyDB_file,)
        historyDB = set(json.load(f))
        f.close()
    except FileNotFoundError as e:
        print("File not found. Using empty history database.")
        return {}
    return historyDB

def loadLinksDB():
    try:
        f = open(linksDB_file,)
        linksDB = set(json.load(f))
        f.close()
    except FileNotFoundError as e:
        print("File not found. Using empty links database.")
        return set()
    return linksDB

try:
    wordDB=wordDB.union(loadWordDB())
    linksDB=loadLinksDB()
    loadHistoryDB()
    browser.get(initialURL)
    browser.execute_script("hideDisc()")
    while (True):
        try:
            searchString=''
            while (searchString == '' or searchString in historyDB):
                searchString=random.choice(tuple(wordDB))
                if (random.randint(1,101) > 80):
                    searchString=searchString+" "+random.choice(tuple(wordDB))
                    if (random.randint(1,101) > 80):
                        searchString=searchString+" "+random.choice(tuple(wordDB))
                if searchString in historyDB:
                    print("Already searched {}".format(searchString))
            inputElement = browser.find_element(by=By.NAME, value="q")
            inputElement.clear()
            inputElement.send_keys(searchString)
            searchButton = browser.find_elements(by=By.ID, value="searchButton")[0]
            searchButton.click()
            time.sleep(random.randint(waitMin,waitMax))
            if extractAllLinks(browser, linksDB, wordDB):
                print("words: {} links: {} search: {}".format(len(wordDB),len(linksDB),searchString))
            else:
                print("words: {} links: {} search: {} ### Not found".format(len(wordDB),len(linksDB),searchString))
            historyDB.add(searchString)
            saveHistoryDB()
            time.sleep(random.randint(waitMin,waitMax))
        except StaleElementReferenceException:
            pass
        except WebDriverException:
            pass
        except IndexError:
            pass
except StaleElementReferenceException:
    pass
except WebDriverException:
    pass
except IndexError:
    pass
