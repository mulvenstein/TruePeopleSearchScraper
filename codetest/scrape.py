# author tom mulvey
# d 7.28.2020

import requests
import re
import sys
import os
import threading
import urllib
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent, FakeUserAgentError  # pip install fake-useragent

base_url = "https://www.truepeoplesearch.com/results?name="

class Person():
    def __init__(self, name, age, livesIn, previousLived, relatives):
        self.name = name
        self.age = age
        self.livesIn = livesIn
        self.previousLived = previousLived
        self.relatives = relatives
    
    def __str__(self):
        s = self.name + "\n" +\
            "Age : " + self.age +\
            "\nLives in " + self.livesIn +\
            "\nUsed to live in " + self.previousLived +\
            "\nRelated to " + self.relatives
        return s

def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    proxies = []
    for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies

def SavePeopleToFile(peopleArr,name):
    s = "RESULTS FOR " + name + "\n------"
    #print(len(peopleArr))
    for i in peopleArr:
        s = s + str(i)
        s = s + "\n-----\n"
    filename = name.replace(" ", "_") + ".txt"
    # if file exists delte, otherwise place res
    if os.path.exists("res/"+filename):
        os.remove("res/"+filename)
    text_file = open("res/"+filename, "w")
    text_file.write(s)
    text_file.close()
    #print(s)
    return True

class ScrapeSite:

    def __init__(self,name):
        '''
        name -> name for first page res on site to be scraped
        '''
        self.name = name
        try:
            self.ua = UserAgent()
        except FakeUserAgentError:
            pass
        # self.proxy = GetUsProxy() was not working
        self.proxies = get_free_proxies() 
        return

    def GetResults(self):
        ''' get first page results from given name '''
        # 1. make url
        url = ""
        try : 
            url = base_url + re.sub(" ", "%20", self.name) #convert name to url friendly
            # print(url)
        except:
            print("\nerror parsing name")
            #exit()
        # 2. send request with random proxy ip and UA
        try:
            proxy = random.choice(self.proxies)
            # p = {"http": proxy, "https": proxy}
            p = {"http": proxy}
            #print(str(p))
            headers = {'User-Agent': self.ua.random}
            session = requests.Session()
            session.proxies = p
            session.headers = headers
            response = session.get(url, timeout=(3,30))
            session.close()
            #response = requests.get(url, proxies=p, headers = headers)

            html = response.text
        except:
            e = sys.exc_info()[0]
            print("\nfailed making proxy request")
            print(e)
            exit()

        PeopleResults=[]
        # 3. use bs4 to parse
        try:
            #print("html = "+html)
            soup = BeautifulSoup(html, "html.parser")
            result_div = soup.find_all('div', attrs = {'class': 'row'})
            i=0
            for r in result_div :
                try:
                    #print(str(i)+"----")
                    name = r.find('div', attrs={'class':'h4'}).get_text()
                    everythingElse = r.find_all('span', attrs={'class':'content-value'})
                    # all other fields are just spans with label 'content-value' so show 
                    # them all in an array then create a person with it
                    res = []
                    #print("NAME : " + name.strip())
                    for j in everythingElse:
                        #print(j.text.strip())
                        res.append(j.text.strip())
                                        
                    # Check to make sure acutal persongrabbed before cont
                    if name != "":
                        p = Person(name, res[0], res[1], res[2], res[3])
                        PeopleResults.append(p)
                        #print(PeopleResults)

                    # Next loop if one element is not present
                    i=i+1

                except:
                    continue

            # SAVE TO FILE RESULTS
            SavePeopleToFile(PeopleResults[1:], self.name)
            #print("")
        except:
            print("bs4 err")
            pass
        

def worker(name):
    print("Running Scrape for " + name + "...")
    scraped = ScrapeSite(name)
    scraped.GetResults()
    print("Finished Scrape for " + name + "...")

def main():
    names = ["Joe Smith", "John Smith", 
    "Amy Smith", "Jeff Smith", "Matt Smith"]
    threads = []

    for i in range(len(names)):
        t = threading.Thread(target=worker, args=(names[i],))
        threads.append(t)
        t.start()

#---
main()