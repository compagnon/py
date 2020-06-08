###############################
# MULTI THREAD ANALYSE / WEB SCRAPING
# From an URLs List
# Use a dedicated HTML Parser
# extract all page and product inside products list
# => looking for  Products information
# if the HTMLPArser stops for whatever reason and do not meet the final html closing tag,
# make an analyse of the raw data
###############################

# https://www.programiz.com/python-programming/
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import abc
import collections
import time

import productwebanalyse as pwa
from dataclasses import dataclass, asdict
from typing import Any

import csv

#Product = collections.namedtuple(
#    'Produit', 'URL Nom Poids Epaisseur Couleur Isolation Prix', defaults=(None,) * 7)
#ProductId = collections.namedtuple('IdProduit', 'URL Nom')


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
    Longueur: int = None
    Complet: bool = False
    Prix: str =None
    Epaisseur: str =None
    Poids: str =None
    Isolation: str =None
    Couleur: str =None


class SaintMacloudProductHTMLParser(pwa.ProductHTMLParser):
    def __init__(self):
        super().__init__()
        self.__analysed = False
        self.__datafield = False
        self.__field = None

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        if not(self.__analysed) and tag == 'div':
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'price-box':
                    self.__analysed = True
        if not(self.__analysed) and tag == 'ul':
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'product-detail-specs':
                    self.__analysed = True                    
        elif self.__analysed and tag == 'meta':
            prix = False
            for attribute in attrs:
                if attribute[0] == 'itemprop' and attribute[1] == 'price':
                    prix = True
                elif attribute[0] == 'content' :
                    content = attribute[1]
            if prix:
                self.set_productData("Prix",content)
        elif self.__analysed and tag == 'tr':
            self.__datafield = True           

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if self.__analysed and (tag == 'div' or tag == 'table'):
            self.__analysed = False
        if self.__datafield and tag == 'tr':
            self.__datafield = False

    def handle_data(self, data):
        if self.__datafield:
            if data == "Epaisseur totale":
                self.__field = "Epaisseur"
            elif data == "Poids au m2":
                self.__field = "Poids"
            elif data == "Isolation acoustique":
                self.__field = "Isolation"
            elif data == "Coloris":
                self.__field = "Couleur"
            elif self.__field != None:
                d = data.strip()
                #print("Encountered some data  :", d, self.__field)
                if d != "":
                    self.set_productData(self.__field,d)
                    self.__field = None
                    self.__datafield = False
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
class SaintMacloudProductListHTMLParser(pwa.ProductsListHTMLParser):
    def __init__(self, productListUrl=None):
        super().__init__(productListUrl)
        self.__article = False
        self.__analysed = False
        self.productParser = SaintMacloudProductHTMLParser()

    def _webanalyse(self, URLName) -> list:
        return self._webanalyseIndexedURL(URLName, 1)

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        if not self.__article and tag == 'ul':
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'products-grid':
                    self.__article = True
        elif self.__article and tag == 'h2':
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'product-name':
                    self.__analysed = True
        elif self.__analysed and tag == 'a':
            url = None
            name = None
            for attribute in attrs:
                if(attribute[0] == 'href'):
                    url = attribute[1]
                if(attribute[0] == 'title'):
                    name = attribute[1]
            p=ProductId(URL=url, Nom=name)
            self.appendProduct(p)
            self.__analysed = False

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__analysed and tag == 'li':
            self.__analysed = False

class LeroyMerlinProductHTMLParser(pwa.ProductHTMLParser):
    def __init__(self):
        super().__init__()
        self.__analysed = False
        self.__datafield = False
        self.__field = None

    def _webanalyseURL(self, URLName) -> list:
        # mettre une temporisation pour eviter d etre considere comme un DoS bot
        time.sleep(5)
        return super()._webanalyseURL(URLName)

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        if not(self.__analysed) and ( tag == 'section' ):
            for attribute in attrs:
                if (attribute[0] == 'class' and attribute[1].startswith('1-price')):
                    self.__analysed = True
                    break
        elif not(self.__analysed) and tag == 'table':
            for attribute in attrs:
                if attribute[0] == 'role' and attribute[1] == 'presentation':
                    self.__analysed = True
                    break
        elif self.__analysed:
            if tag == 'span':
                for attribute in attrs:
                    if (attribute[0] == 'class' and attribute[1].startswith('-a-priceAmount')):
                        self.__datafield = True
                        self.__field = "Prix"
                        break
            elif tag == 'th':
                for attribute in attrs:
                    if attribute[0] == 'class' and attribute[1] == 'a-attrName':
                        self.__datafield = True
                        break                  

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if self.__analysed and self.__datafield and self.__field == None:
            self.__datafield = False
        if self.__analysed and tag == 'section':
            self.__analysed = False

    def handle_data(self, data):
        if self.__datafield:
            if self.__field == None:
                if data == "Hauteur des fibres (en mm)":
                    self.__field = "Epaisseur"
                elif data == "Poids total (en g/m²)":
                    self.__field = "Poids"
                elif data == "Isolation phonique (en dB)":
                    self.__field = "Isolation"
                elif data == "Couleur":
                    self.__field = "Couleur"
            else:
                d = data.strip()
                #print("Encountered some data  :", d, self.__field)
                if d != "":
                    self.set_productData(self.__field,d)
                    self.__field = None
                    self.__datafield = False
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

class LeroyMerlinProductListHTMLParser(pwa.ProductsListHTMLParser):
    def __init__(self, productListUrl=None):
        super().__init__(productListUrl)
        self.__article = False
        self.__analysed = False
        self.url = None
        self.nom = None
        self.productParser = LeroyMerlinProductHTMLParser()

    def _webanalyse(self, URLName) -> list:
        # mettre une temporisation pour eviter d etre considere comme un DoS bot
        time.sleep(10)
        return self._webanalyseIndexedURL(URLName,2)

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        if not self.__article and tag == 'article':
            #print("Encountered a start tag:", tag, attrs)
            self.__article = True
        elif self.__article and tag == 'div':
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'kl-blade':
                    self.__analysed = True
        elif self.__analysed and tag == 'a':
            # print(attrs)
            if(attrs[0][0] == 'href'):
                self.url = 'https://www.leroymerlin.fr'+ attrs[0][1]
                    
    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__analysed and tag == 'a':
            self.__article = False
            self.__analysed = False
            self.appendProduct(ProductId(URL=self.url, Nom=self.nom))

    def handle_data(self, data):
        if self.__analysed:
            self.nom = data.strip() 

class EspaceRevetementProductHTMLParser(pwa.ProductHTMLParser):
    def __init__(self):
        super().__init__()
        self.__analysed = False
        self.__datafield = False
        self.__field = None

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        if not(self.__analysed) and tag == 'section':
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'product-features':
                    self.__analysed = True
        elif self.__analysed:
            if tag == 'dt':
                for attribute in attrs:
                    if attribute[0] == 'class' and attribute[1] == 'name':
                        self.__datafield = True

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if self.__analysed and tag == 'section':
            self.__analysed = False
            self.__datafield = False

    def handle_data(self, data):
        if self.__datafield:
            if data == "Epaisseur totale" or data == "Epaisseur":
                self.__field = "Epaisseur"
            elif data == "Poids":
                self.__field = "Poids"
            elif data == "Isolation phonique":
                self.__field = "Isolation"
            elif data == "Couleur":
                self.__field = "Couleur"
            else:
                d = data.strip()
                #print("Encountered some data  :", d, self.__field)
                if self.__field != None and d != "":
                    self.set_productData(self.__field,d)
                    self.__field = None
                    self.__datafield = False
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

class EspaceRevetementProductListHTMLParser(pwa.ProductsListHTMLParser):
    def __init__(self, productListUrl=None):
        super().__init__(productListUrl)
        self.__article = False
        self.__analysed = False
        self.productParser = EspaceRevetementProductHTMLParser()

    def _webanalyse(self, URLName) -> list:
        return self._webanalyseIndexedURL(URLName, 1)

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        if not self.__article and tag == 'article':
            #print("Encountered a start tag:", tag, attrs)
             self.__article = True
        elif self.__article and tag == 'h1':
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'h3 product-title':
                    self.__analysed = True
        elif self.__analysed and tag == 'a':
            # print(attrs)
            if(attrs[0][0] == 'href') and attrs[1][0] == 'title':
                url = attrs[0][1]
                name = attrs[1][1]
                self.appendProduct(ProductId(URL=url, Nom=name))                
                    
    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__article and tag == 'article':
            self.__article = False
            self.__analysed = False

class BricoflorProductHTMLParser(pwa.ProductHTMLParser):

    def __init__(self):
        super().__init__()
        self.__analysed = False
        self.__datafield = False
        self.__field = None

    # return a list of Products
    def _webanalyse(self, URLName) -> list:
        return self._webanalyseIndexedURL(URLName)

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        if not(self.__analysed) and tag == 'table':
            for attribute in attrs:
                if attribute[0] == 'id' and attribute[1] == 'product-attribute-specs-table':
                    self.__analysed = True
        elif self.__analysed:
            if tag == 'span':
                for attribute in attrs:
                    if attribute[0] == 'class' and attribute[1] == 'label':
                        self.__datafield = True
        elif tag == 'div' and len(attrs) == 1 and attrs[0][0] == 'class' and attrs[0][1] == 'baseprice-box':
            self.__datafield = True
            self.__field = "Prix"

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if self.__analysed and tag == 'table':
            self.__analysed = False
            self.__datafield = False

    def handle_data(self, data):
        if self.__datafield:
            if data == "Épaisseur totale":
                self.__field = "Epaisseur"
            elif data == "Poids total":
                self.__field = "Poids"
            elif data == "Isolation phonique aux bruits d'impacts":
                self.__field = "Isolation"
            elif data == "Couleur":
                self.__field = "Couleur"
            else:
                d = data.strip()
                #print("Encountered some data  :", d, self.__field)
                if self.__field != None and d != "":
                    self.set_productData(self.__field,d)
                    self.__field = None
                    self.__datafield = False

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

class BricoflorProductListHTMLParser(pwa.ProductsListHTMLParser):
    """Parser Class pour Bricoflor"""
    def __init__(self, productListUrl=None):
        super().__init__(productListUrl)
        self.__analysed = 0
        self.productParser = BricoflorProductHTMLParser()
    
    def _webanalyse(self, URLName) -> list:
        return self._webanalyseIndexedURL(URLName,1)

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        if self.__analysed == 0 and tag == 'ul':
            #print("Encountered a start tag:", tag, attrs)
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'products-grid row large-products-grid':
                    self.__analysed = self.__analysed + 1
        elif self.__analysed > 0 and tag == 'ul':
            self.__analysed = self.__analysed + 1
        elif self.__analysed > 0 and tag == 'a':
            # print(attrs)
            if(attrs[0][0] == 'href') and attrs[1][0] == 'title':
                url = attrs[0][1]
                name = attrs[1][1]
                self.appendProduct(ProductId(URL=url, Nom=name))                
                    
    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__analysed > 0 and tag == 'ul':
            self.__analysed = self.__analysed - 1


# Main inputs
# URL Liste

InputsList2 = [('IndexURL__', BricoflorProductListHTMLParser(), 'https://www.bricoflor.fr/sol/moquette.html?p={}'),
               ('FixedURL', EspaceRevetementProductListHTMLParser(
               ), 'https://www.espacerevetements.com/index.php?id_category=17&controller=category'),
               ('OffsetURL', LeroyMerlinProductListHTMLParser(), 'https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?resultOffset={0}&resultLimit={99}&resultListShape=MOSAIC&priceStyle=SALEUNIT_PRICE')]

InputsList = [
#    BricoflorProductListHTMLParser('https://www.bricoflor.fr/sol/moquette.html?p={}')]
#            EspaceRevetementProductListHTMLParser('https://www.espacerevetements.com/index.php?controller=category&id_category=17&page={}')]
            LeroyMerlinProductListHTMLParser('https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?page={}')]
#            SaintMacloudProductListHTMLParser('https://www.saint-maclou.com/collection-sols/moquette.html?p={}')]
productsList = list()
numberOfProduct = 0

with open('products.csv', mode='w') as products_file:
    products_writer= csv.writer(products_file, )
    products_writer = csv.DictWriter(products_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=['URL','Nom','Contenu','Longueur','Complet','Prix','Epaisseur','Poids','Isolation','Couleur'])
    products_writer.writeheader()
    for parser in InputsList:
        print(parser)
        for product in parser.productsList:        
            print(product)
            products_writer.writerow(asdict(product))
            numberOfProduct = numberOfProduct + 1
            productsList.append(product)
    print('NumberOfProduct', numberOfProduct)