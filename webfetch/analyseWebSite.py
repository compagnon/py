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
import productwebanalyse as pwa
Product = collections.namedtuple(
    'Produit', 'URL Nom Poids Epaisseur Couleur Isolation Prix', defaults=(None,) * 7)
ProductId = collections.namedtuple('IdProduit', 'URL Nom')


class LeroyMerlinProductHTMLParser(pwa.ProductHTMLParser):
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
                if attribute[0] == 'class' and attribute[1] == '1-mainPrice':
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
                    if attribute[0] == 'class' and attribute[1] == '-a-priceAmount -fontTitle2 -fontFamilyBold':
                        self.__datafield = True
                        self.__field = "Prix"
                        break
            elif tag == 'td':
                for attribute in attrs:
                    if attribute[0] == 'class' and attribute[1] == 'a-attrName':
                        self.__datafield = True
                        break


    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if self.__analysed and tag in ( 'div', 'table'):
            self.__analysed = False
            self.__datafield = False

    def handle_data(self, data):
        if self.__datafield:
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
                if self.__field != None and d != "":
                    self.set_productData(self.__field,d)
                    self.__field = None
                    self.__datafield = False

class LeroyMerlinProductListHTMLParser(pwa.ProductsListHTMLParser):
    def __init__(self, productListUrl=None):
        super().__init__(productListUrl)
        self.__article = False
        self.__analysed = False
        self.productParser = EspaceRevetementProductHTMLParser()

    def _webanalyse(self, URLName) -> list:
        return self._webanalyseSlotURL(URLName,0,99)

    # implements parsing methods
    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        if not self.__article and tag == 'div':
            #print("Encountered a start tag:", tag, attrs)
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == 'prd':
                    self.__article = True
        elif self.__article and tag == 'h3':
            for attribute in attrs:
                if attribute[0] == 'class' and attribute[1] == '':
                    self.__analysed = True
        elif self.__analysed and tag == 'a':
            # print(attrs)
            if(attrs[0][0] == 'href'):
                url = 'https://www.leroymerlin.fr'+ attrs[0][1]
                self.appendProduct(ProductId(URL=url, Nom=None))                
                    
    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__article and tag == 'div':
            self.__article = False
            self.__analysed = False

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
#    BricoflorProductListHTMLParser(
#    'https://www.bricoflor.fr/sol/moquette.html?p={}')]
#            EspaceRevetementProductListHTMLParser('https://www.espacerevetements.com/index.php?controller=category&id_category=17&page={}'),
            LeroyMerlinProductListHTMLParser('https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?resultOffset={}&resultLimit={}&resultListShape=MOSAIC&priceStyle=SALEUNIT_PRICE')]

productsList = list()
numberOfProduct = 0


for parser in InputsList:
    print(parser)
    for product in parser.productsList:
        print(product)
        numberOfProduct = numberOfProduct + 1
        productsList.append(product)
print('NumberOfProduct', numberOfProduct)
