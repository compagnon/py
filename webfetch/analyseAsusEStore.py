###############################
# From an URLs List
# Use a dedicated HTML Parser
# extract Products information
# display tabular data
###############################

# https://www.programiz.com/python-programming/
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import abc
import collections
import time

import productwebanalyse as pwa
ProductId = collections.namedtuple('IdProduit', 'URL Nom')

Product = collections.namedtuple(
    'Produit', 'URL Nom Contenu', defaults=(None,) * 3)

class AsusProductHTMLParser(pwa.ProductHTMLParser):

    def __init__(self):
        super().__init__()
        self.__analysed = False 

    def _webanalyse(self, URLName) -> list:
        return self._webanalyseIndexedURL(URLName)

   # implements parsing methods
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        if tag == 'img':
            for attribute in attrs:
                if attribute[0] == 'title' and attribute[1].startswith('oeuf'):
                    self.__analysed = True

    def handle_data(self, data):
        if self.__analysed:
            d = data.strip()
            if d.startswith('Code pour récupérer le cadeau'):
                self.set_productData("Contenu",data)

class AsusProductListHTMLParser(pwa.ProductsListHTMLParser):
    """Parser Class pour Asus estore"""
    def __init__(self, productListUrl=None, nbPages=1):
        super().__init__(productListUrl)
        self.__analysed = 0
        self.__nbPages = nbPages
        self.productParser = AsusProductHTMLParser()
    
    def _webanalyse(self, URLName) -> list:
        # mettre une temporisation pour eviter d etre considere comme un DoS bot
        time.sleep(1)
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


# Main inputs
# URL Liste

InputsList2 = [            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/gaming/tous-les-pc-gaming',3),]

InputsList = [
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/smartphone-asus/accessoires-smartphones'),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/smartphone-asus/tous-les-smartphones'),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/smartphone-asus/smartphones-reconditionnes'),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/gaming/tous-les-pc-gaming',3),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/gaming/pc-portable-reconditionne-serie-rog',3),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/gaming/accessoire-gaming'),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/gaming/rog-phone-new'),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/pc-de-bureau/tous-les-pc-fixes-et-all-in-one'),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/pc-asus/ordinateurs-portables',5),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/pc-asus/pc-portables-avec-screenpad-screenpad-plus-et-numpad'),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/pc-asus/extensions-de-garantie'),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/pc-asus/pc-portable-reconditionne',6),
            AsusProductListHTMLParser('https://eshop.asus.com/fr-FR/offres-du-moment/vivez-l-experience-all-in-one'),
            ]
productsList = list()
numberOfProduct = 0


for parser in InputsList:
    print(parser)
    for product in parser.productsList:
        print ('.', end=" ")
        if product.Contenu != None: 
            print(product)
            
        numberOfProduct = numberOfProduct + 1
        productsList.append(product)
print('NumberOfProduct', numberOfProduct)
