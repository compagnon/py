###############################
# MULTI THREAD ANALYSE / WEB SCRAPING
# example of code for analysing URLs, a URL(productsList) can contain other link to other URLS (products). objective is to find an eastern egg!
# 
# From an URLs List
# Use a dedicated HTML Parser to get a Products list
# extract all page and product inside products list
# => looking for an special image or a tag  a code
# if the HTMLPArser stops for whatever reason and do not meet the final html closing tag,
# make an analyse of the raw data
###############################

# https://www.programiz.com/python-programming/
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import abc
import collections
import time
import datetime
import random
import threading

import productwebanalyse as pwa
from dataclasses import dataclass
from typing import Any


@dataclass
class ProductId:
    URL: str
    Nom: str = None

#ProductId = collections.namedtuple('IdProduit', 'URL Nom')

#Product = collections.namedtuple(
#    'Produit', 'URL Nom Contenu Longueur Complet', defaults=(None,) * 5)
@dataclass
class Product:
    URL: str
    Nom: str = None
    Contenu: str = None
    Longueur: int = None
    Parsed: bool = False

class TemplateSiteProductHTMLParser(pwa.ProductHTMLParser):

    def __init__(self):
        super().__init__()

    # return a list of Products
    def _webanalyse(self, URLName) -> list:
        #could add a latency to avoid being taken as a robot ...
        #time.sleep(random.randint(5,30))
        return self._webanalyseIndexedURL(URLName)

    def _analyseRaw(self,data):
        begin = data.find("Code pour récupérer le cadeau : ")
        if begin != -1 :
            self.set_productData("Contenu",data[begin:begin+8])

    # populate the product object/dictionnary with data
    def feed(self, data) -> list:
        #optimize : rescan if the lenght is different
        l = len(data)
        p = super().get_product()
        if( l != p.get('Longueur',-1) ):
            p = super().feed(data)
            productTuple = Product(**p)
            p['Longueur'] = l

        productTuple = Product(**p)
        return [productTuple]

   # implements parsing methods
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        if tag == 'img':
            for attribute in attrs:
                if attribute[0] == 'title' and attribute[1].startswith('oeuf'):
                    self.set_productData("Contenu","oeuf")
                    self.__analysed = True

    def handle_data(self, data):
#        if self.__analysed:
        d = data.strip()
        if d.startswith('Code pour récupérer le cadeau'):
            self.set_productData("Contenu",data[len("Code pour récupérer le cadeau : "):])

    def handle_endtag(self, tag):
        if tag == 'html':
            self.setCompleted()
            self.set_productData("Parsed",True)

class TemplateSiteProductListHTMLParser(pwa.ProductsListHTMLParser):
    """Parser Class for the products list"""
    def __init__(self, productListUrl=None, nbPages=1):
        super().__init__(productListUrl)
        self.__analysed = 0
        self.__nbPages = nbPages
        self.productParser = TemplateSiteProductHTMLParser()
    
    # choose how the list navigation pages are implemented
    # return a list of 
    def _webanalyse(self, URLName) -> list:
        # add a latency , to avoid being taken for a bot and DoS
        #time.sleep(random.randint(5,30))
        return self._webanalyseEndedIndexedURL(URLName,'?p=',1,self.__nbPages)

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        if self.__analysed == 0 and tag == 'article':
            #print("Encountered a start tag:", tag, attrs)
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'product':
                    self.__analysed = self.__analysed + 1
        elif self.__analysed > 0 and tag == 'a':
            # print(attrs)
            found = False
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'link-primary':
                    found = True
                elif attribute[0] == 'href':
                    url = attribute[1]
                elif attribute[0] == 'title':
                    name = attribute[1]
            if found:
                self.appendProduct(ProductId(URL=url, Nom=name))
                    
    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__analysed > 0 and tag == 'article':
            self.__analysed = self.__analysed - 1


"""take a list of ProductsListParser , and return the products (URL"""
def scanProductsSite(InputsList, productsList):
    numberOfProduct = 0
    for parser in InputsList:
        for product in parser.productsList:
            if product != None :
                numberOfProduct = numberOfProduct + 1
                productsList.append(product)

    print('scanProductsSite NumberOfProducts: ', numberOfProduct)

"""take a list of StandaloneURL , and return the products """
def scanStandaloneSite(InputsList, productsList):
    numberOfProduct = 0
    standaloneParser = TemplateSiteProductHTMLParser()
    # Scan standalone page
    for url in InputsList:
        pid = ProductId(URL=url.URL)
        standaloneParser.set_product(pid)
        for prod in standaloneParser._webanalyseURL(pid.URL):
            if prod != None :
                productsList.append(prod)
                numberOfProduct = numberOfProduct + 1
            standaloneParser.reset()

    print('scanStandaloneSite NumberOfProducts: ', numberOfProduct)

#task  surveillant la page de l oeuf existante, et si elle disparait, rendre les taches de recherche de l oeuf suivant plus agressives
class GoRunner(threading.Thread):

    def __init__(self, threadID, product, delay, threads, pill2kill):
        threading.Thread.__init__(self,args=(pill2kill,threadID))
        self.__threadID = threadID
        self.__product = product
        self.__delay = delay
        self.__standaloneParser = TemplateSiteProductHTMLParser()
        self.__standaloneParser.product = product
        self.__threads = threads
        self.__pill2kill = pill2kill        
    
    def run(self):
        print ("Starting Survey Egg",str(self.__threadID)," ",self.__product.URL)
        self.__stop = False
        self.rescanExistingEggURL()
        print ("Exiting Survey Egg",str(self.__threadID)," ",self.__product.URL)

    # Define a function for the thread
    def rescanExistingEggURL(self):
        count = 0
        try:
            while not self.__stop:
                time.sleep(self.__delay)

                for prod in self.__standaloneParser._webanalyseURL(self.__product.URL):
                    if prod != None and prod.Contenu == None:
                        self.stop()

                count += 1

#                if count > random.randint(10,100): 
#                    self.stop()
        except:
            #pass
            print("error ", self.__threadID, ' count', count)
        self.accelerateAllthreads()

    def set_delay(self, d):
        print ("change Delay ",self.__threadID)
        self.__delay = d

    def stop(self):
        print ("Stop ",self.__threadID)        
        self.__stop = True

    def accelerateAllthreads(self):     
        for t in self.__threads:
            t.set_delay(1)          


#Taches de recherche d oeuf dans les autres pages
class SearchRunner(threading.Thread):

    def __init__(self, threadID, product, delay, threads, pill2kill):
        threading.Thread.__init__(self,args=(pill2kill,threadID))
        self.__threadID = threadID
        self.__product = product
        self.__delay = delay
        self.__standaloneParser = TemplateSiteProductHTMLParser()
        self.__standaloneParser.set_product(product)
        self.__threads = threads
        self.__pill2kill = pill2kill
    
    def run(self):
        print ("Starting ",str(self.__threadID)," ",self.__product.URL)
        self.__stop = False
        self.rescanProductURL()
        print ("Exiting ",str(self.__threadID)," ",self.__product.URL)

    # Define a function for the thread
    def rescanProductURL(self):
        count = 0
        while not self.__stop:
            time.sleep(self.__delay)

            try:
                for prod in self.__standaloneParser._webanalyseURL(self.__product.URL):
                    if prod != None and prod.Contenu != None:
                        #contenu trouvé
                        print(prod.Contenu)
                        self.__product.Contenu = prod.Contenu
                        self.stopAllthreads()

                count += 1
#                if count > random.randint(5,10):
#                    self.__product.Contenu = 'TEST '+ str(self.__threadID)
#                    self.stopAllthreads()
            except BaseException as e:
                print("error ", self.__threadID, ' count', count, e)
                self.__standaloneParser = TemplateSiteProductHTMLParser()
                self.__standaloneParser.set_product(self.__product)
        print("Stop ", self.__threadID, ' count', count)


    def set_delay(self, d):
        print ("change Delay ",self.__threadID)
        self.__delay = d

    def stop(self):
        print ("Stop ",self.__threadID)
        self.__stop = True
    
    def stopAllthreads(self):
        for t in self.__threads:            
            t.stop()        
        self.__pill2kill.set()


# Main inputs
# URL Liste

#logginEstore('0XS6GNRQ')

##STOP

productsList = list()

InputsList = [            TemplateSiteProductListHTMLParser('https://eshop.asus.com/fr-FR/pc-de-bureau/pc-de-bureau-gaming')]

#other pages to analyse
OthersList = [ ProductId(URL='https://eshop.asus.com/fr-FR/faq') ]


foundEggProduct = None
threads = []
# build the list of URL to scan
scanProductsSite(InputsList,productsList)
#read /scan the urls of list of urls
scanStandaloneSite(OthersList,productsList)
scanStandaloneSite(InputsList,productsList)
# in productsList, a runner is set for analysing a single URL

#print ('.', end='',flush=True)

threadID = 0
pill2kill = threading.Event()
for product in productsList:
    threadID += 1

    if product.Contenu != None :
        t = GoRunner( str(threadID), product, 1,threads,pill2kill)
        #debug
        #product.Contenu = None
        #t = EggSearchRunner( str(threadID), product, 10,threads,pill2kill)
    else:
        t = SearchRunner( str(threadID), product, 10,threads,pill2kill)
    threads.append(t)

#start all
for t in threads:
    t.start()

# Wait for all threads to complete
for t in threads:
   t.join()

print ("Exiting Main Thread")
print('time.time:', datetime.datetime.now())

for product in productsList:
    if product.Contenu != None :
        foundEggProduct = product
        
        #get the code and cart it
        code = foundEggProduct.Contenu
        print(code)
        print(foundEggProduct)


