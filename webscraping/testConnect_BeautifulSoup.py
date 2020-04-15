import os
import csv
import requests
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError



def getHiddenValue(html,htmlInstruction,valueLen):
    begin = html.find(htmlInstruction) + len(htmlInstruction)
    return html[begin:begin+valueLen]

def logginEstore(code):
    url1 = 'https://account.asus.com/signin.aspx?lang=fr-fr&site=fr'
    req = Request(url1)
    resp = urlopen(req)
    html = resp.read().decode('utf-8')


    soup = BeautifulSoup(html)
    hidden_tags = soup.find_all("input", type="hidden")
    data = dict()
    for tag in hidden_tags:
        print(tag.attrs)
        data[tag.attrs['id']]  = tag.attrs.get('value','')

    skey = getHiddenValue(html,"<form name=\"aspnetForm\" method=\"post\" action=\"./loginform.aspx?skey=",len('6d97e0e4b1264b5ab7a92a65e86c4d12'))


    url = 'https://account.asus.com/loginform.aspx?skey='+skey
    data['Front_txtAccountID'] =  'XXX@xxx.com'
    data['Front_txtPassword'] =  'xx'


    data = urlencode(data)
    data = data.encode('ascii')
    resp = requests.post(url,data=data)
    #req = Request (url,data=data) # this will make the method "POST"
    #resp = urlopen(req)
    #html = resp.read().decode('utf-8')
    html = resp.text


    url2 = 'https://eshop.asus.com/fr-FR/casque-tuf-gaming-h5-lite.html'

    url3 = 'https://eshop.asus.com/fr-FR/checkout/cart/add/uenc/aHR0cHM6Ly9lc2hvcC5hc3VzLmNvbS9mci1GUi9jYXNxdWUtdHVmLWdhbWluZy1oNS1saXRlLmh0bWw_X19fU0lEPVU,/product/7742/form_key/LgHxOovvOZw67UOZ/'
    data3 = {'form_key' : 'LgHxOovvOZw67UOZ',
            'product'  : '7742'}


logginEstore('TEST')

requete = requests.get("https://url")
page = requete.content
soup = BeautifulSoup(page)

h1 = soup.find("h1", {"class": "page_title"})
print(h1.string)