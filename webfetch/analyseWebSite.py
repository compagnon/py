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
Product = collections.namedtuple(
    'Produit', 'URL Nom Poids Epaisseur Couleur Isolation Prix', defaults=(None,) * 7)
ProductId = collections.namedtuple('IdProduit', 'URL Nom')

###############################
# CLASS DEFINITION
# URLHTML Parser for providing several config using index inside URL
# PRODUCTS LIST HTML PARSER for parsing an URL containing a PRODUCT LIST
# PRODUCT HTML PARSER for parsing an
###############################
class URLHTMLParser(HTMLParser):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _webanalyse(self, url) -> list:
        pass 

    def _webanalyseURL(self, url) -> list:
        """ return list if the url is providing a collection or just one product """
        req = Request(url)
        try:
            response = urlopen(req)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            return None
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
            return None
        else:
            # la page existe, analyser la page avec un Parseur HTML
            html = response.read().decode('utf-8')
            return self.feed(html)

    def _webanalyseIndexedURL(self, URLName, begin) -> list:
        return self._webanalyseSlotURL(URLName,begin,1)

    def _webanalyseSlotURL(self, URLName, begin, offset) -> list:
        """ return yield list if the url is providing new data """
        """retry some times if no new data is provided"""
        i = begin
        retry = 2  # si 2 pages sont identiques, faire un increment de l index pour le nb de retry
        while True:
            url = URLName.format(i,offset)
            print(url)
            p = self._webanalyseURL(url)
            i = i + offset
            if p == None or len(p) == 0:
                if(retry == 0):
                    break
                else:
                    retry = retry - 1
            else:
                for n in p:
                    yield n
        return None

class ProductHTMLParser(URLHTMLParser):
    def __init__(self):
        super().__init__()
        self.__product = dict()

    def set_productId(self, id):
        self.__product = id._asdict()

    def set_productData(self, key, data):
        self.__product[key] = data        

    productId = property(fget=None, fset=set_productId, fdel=None, doc=None)

    def feed(self, data) -> list:
        super().feed(data)
        productTuple = Product(**self.__product)
        self.__product.clear()
        return [productTuple]


class ProductsListHTMLParser(URLHTMLParser):


    def __init__(self, productListUrl=None):
        super().__init__()
        self.__productsId = None
        self.__productsIdTotal = {}
        self.URL = productListUrl
        self.__productParser = None

    def get_productParser(self):
        return self.__productParser

    def set_productParser(self, productparser):
        self.__productParser = productparser

    def appendProduct(self, pid):
        if(self.__productsIdTotal.get(pid.URL) == None):
            self.__productsId.append(pid)
            self.__productsIdTotal[pid.URL] = pid

    def get_products(self) -> list:
        for pid in self._webanalyse(self.URL):
            # analyse the product thx to its id
            self.productParser.set_productId(pid)
            for p in self.productParser._webanalyseURL(pid.URL):
                yield p

    productsList = property(get_products, fset=None, fdel=None, doc=None)
    productParser = property(
        get_productParser, fset=set_productParser, fdel=None, doc=None)

    def feed(self, data) -> list:
        total = len(self.__productsIdTotal)
        self.__productsId = []
        super().feed(data)
        current = len(self.__productsId)
        print('nb de produits apres analyse:', total, ' (+ ', current, ')')
        return self.__productsId


class LeroyMerlinProductHTMLParser(ProductHTMLParser):
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
            else:
                d = data.strip()
                #print("Encountered some data  :", d, self.__field)
                if self.__field != None and d != "":
                    self.set_productData(self.__field,d)
                    self.__field = None
                    self.__datafield = False

class LeroyMerlinProductListHTMLParser(ProductsListHTMLParser):
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


class EspaceRevetementProductHTMLParser(ProductHTMLParser):
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
            else:
                d = data.strip()
                #print("Encountered some data  :", d, self.__field)
                if self.__field != None and d != "":
                    self.set_productData(self.__field,d)
                    self.__field = None
                    self.__datafield = False

class EspaceRevetementProductListHTMLParser(ProductsListHTMLParser):
    def __init__(self, productListUrl=None):
        super().__init__(productListUrl)
        self.__article = False
        self.__analysed = False
        self.productParser = EspaceRevetementProductHTMLParser()

    def _webanalyse(self, URLName) -> list:
        return self._webanalyseIndexedURL(URLName)

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

class BricoflorProductHTMLParser(ProductHTMLParser):

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
            else:
                d = data.strip()
                #print("Encountered some data  :", d, self.__field)
                if self.__field != None and d != "":
                    self.set_productData(self.__field,d)
                    self.__field = None
                    self.__datafield = False


class BricoflorProductListHTMLParser(ProductsListHTMLParser):
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
    BricoflorProductListHTMLParser(
    'https://www.bricoflor.fr/sol/moquette.html?p={}')]
#            EspaceRevetementProductListHTMLParser('https://www.espacerevetements.com/index.php?controller=category&id_category=17&page={}')]
#            LeroyMerlinProductListHTMLParser('https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?resultOffset={}&resultLimit={}&resultListShape=MOSAIC&priceStyle=SALEUNIT_PRICE')]


productsList = list()
numberOfProduct = 0


for parser in InputsList:
    print(parser)
    for product in parser.productsList:
        print(product)
        numberOfProduct = numberOfProduct + 1
        productsList.append(product)
print('NumberOfProduct', numberOfProduct)

"""
for configType in InputsList:
    print (configType[0])
    if configType[0] == 'IndexURL':
        listParser = HTMLParser(configType[1])
        productParser = HTMLParser(listParser.productParser)
        if webanalyseIndexedURL(instanceParser=listParser, URLName=configType[2]):
            #print(configType[1].productsIdList)
            for productId in listParser.productsIdList:
#                print("Analyse Produit",productId)
                configType[1].productParser.productId = productId
                if webanalyseURL(configType[1].productParser,productId.URL) :
                    numberOfProduct = numberOfProduct + 1
                    productsList.append()
                    print(configType[1].productParser.product)
        print('NnumberOfProduct',numberOfProduct)

    elif configType[0] == 'FixedURL':
        if webanalyseFixedURL(configType[1],configType[2]):
            #print(configType[1].productsIdList)
        #                productId = ProductId(URL='https://www.espacerevetements.com/index.php?id_category=17&controller=category', Nom='Vorwerk Safira "8H74"')
    elif configType[0] == 'OffsetURL':
        pass
"""
