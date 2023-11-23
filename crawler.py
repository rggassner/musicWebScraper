#!/usr/bin/python3
import json
import random
import requests
import hashlib
import os
import signal
from bs4 import BeautifulSoup

url_prefix="https://yoursite/"
word_db_default=set({'prodigy'})
word_db_file="word_db_file.json"
history_db_file="history_db_file.json"
log_file="navigation.log"
iterations=1
songs_folder='download'
MAX_DOWNLOAD_TIME = 600

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
        raise TypeError

def load_json_file(file):
    try:
        f = open(file,)
        db = set(json.load(f))
        f.close()
    except FileNotFoundError as e:
        print("File not found. Using empty history database.")
        return set({})
    return db

def save_json_file(filename,content):
    with open(filename, 'w') as outfile:
        result=json.dumps(content,default=set_default)
        outfile.write(result)

def pick_query(word_db,history_db):
    ntry=0
    query=''
    while (query == '' or query in history_db):
        query=random.choice(tuple(word_db))
        if (random.randint(1,11) > 8):
            query=query+" "+random.choice(tuple(word_db))
            if (random.randint(1,11) > 8):
                query=query+" "+random.choice(tuple(word_db))
        ntry+=1
    return query

def get_words(soup):
    output = []
    classes=["artist-name","track-name"]
    for cname in classes:
        instances = soup.find_all("div", class_=cname)
        for instance  in instances:
            output.extend(instance.get_text().split())
    return set(output)

def break_after(seconds=60):
    def timeout_handler(signum, frame):  # Custom signal handler
        raise TimeoutException

    def function(function):
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                res = function(*args, **kwargs)
                signal.alarm(0)  # Clear alarm
                return res
            except TimeoutException:
                print(
                    "Oops, timeout: {} {} {} {} sec reached.".format(
                        seconds, function.__name__, args, kwargs
                    )
                )
            return
        return wrapper
    return function

@break_after(MAX_DOWNLOAD_TIME)
def download(link):
    directory=hashlib.md5(link.encode()).hexdigest()[0:2]
    dir_exists = os.path.exists(songs_folder+'/'+directory)
    if not dir_exists:
        os.makedirs(songs_folder+'/'+directory)
    filename=hashlib.md5(link.encode()).hexdigest()
    print('Downloading {}'.format(link))
    r = requests.get('https:'+link, allow_redirects=False)
    open(songs_folder+'/'+directory+'/'+filename+'.mp3', 'wb').write(r.content)

def save_log(soup):
    songs = soup.find_all("div", class_="f-table")
    for song in songs:
        url=song.find_all("a", class_="mp3")[0]['href']
        artist=song.find_all('div',class_='artist-name')[0].get_text()
        track=song.find_all('div',class_='track-name')[0].get_text()
        filename=hashlib.md5(url.encode()).hexdigest()
        with open(log_file, "a") as myfile:
            myfile.write("{},{},{}\n".format(filename,artist,track))

def navigate_query(query,word_db):
    mp3list=[]
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    page=requests.get(url_prefix+query, headers=header).text
    soup = BeautifulSoup(page, 'html.parser')
    save_log(soup)
    mp3urls = soup.find_all("a", class_="mp3")
    for mp3url in mp3urls:
        mp3list.append(mp3url['href'])
    word_db=word_db.union(get_words(soup))
    npages=len(soup.find_all("div", class_="inactive-p"))
    while npages > 0:
        page=requests.get(url_prefix+query+'/'+str(npages+1), headers=header).text
        soup = BeautifulSoup(page, 'html.parser')
        save_log(soup)
        mp3urls = soup.find_all("a", class_="mp3")
        for mp3url in mp3urls:
            mp3list.append(mp3url['href'])
        word_db=word_db.union(get_words(soup))
        npages-=1
    count=0
    for mp3url in mp3list:
        download(mp3url)
        count+=1
    save_json_file(word_db_file,word_db)

def crawl(n_searches):
    while n_searches>0:
        word_db=load_json_file(word_db_file)
        if len(word_db) == 0:
            word_db=word_db_default
        history_db=load_json_file(history_db_file)
        query=pick_query(word_db,history_db)
        print('Query {}'.format(query))
        navigate_query(query,word_db)
        n_searches-=1
        history_db.add(query)
        save_json_file(history_db_file,history_db)

def main():
    crawl(iterations)

if __name__ == "__main__":
    main()
