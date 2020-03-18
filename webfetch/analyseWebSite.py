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
import collections
Product = collections.namedtuple('Produit', 'URL Nom Poids Epaisseur Couleur Isolation Prix', defaults=(None,) * 7)
ProductId = collections.namedtuple('IdProduit', 'URL Nom')

###############################
## CLASS DEFINITION
## PRODUCTS LIST HTML PARSER for parsing an URL containing a PRODUCT LIST
## PRODUCT HTML PARSER for parsing an  
###############################
class LeroyMerlinProductListHTMLParser(HTMLParser):
    def __init__(self, productListUrl = None):
        pass
    

class EspaceRevetementProductListHTMLParser(HTMLParser):
    def __init__(self, productListUrl = None):
        pass

class BricoflorProductHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.__analysed = False
        self.__datafield = False
        self.__field = None
        self.__product = dict()
        self.__productTuple = None

    def set_productId(self,id):
        self.__product = id._asdict()

    productId = property(fget=None, fset=set_productId,fdel=None,doc=None)

    def feed(self, data) -> list:
        super().feed(data)
        self.__productTuple = Product(**self.__product)
        self.__product.clear()
        return [self.__productTuple]
        
    #implements parsing methods
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
                if self.__field != None and d != "" :
                    #print(data)
                    self.__product[self.__field]=d
                    self.__field = None
                    self.__datafield = False


class BricoflorProductListHTMLParser(HTMLParser):
    """Parser Class pour Bricoflor"""
    def __init__(self, productListUrl = None):
        super().__init__()
        self.__analysed = 0
        self.__numberOfProducts = 0
        self.__productsIdTotal = {}
        self.URL = productListUrl
        self.__productParser = BricoflorProductHTMLParser()

    def get_productParser(self):
        return self.__productParser

    def get_products(self) -> list:
        for pid in _webanalyseIndexedURL(self,self.URL):
            # analyse the product thx to its id
            self.productParser.set_productId(pid)
            for p in _webanalyseURL(self.productParser, pid.URL):
                yield p

    productsList = property(get_products, fset=None,fdel=None,doc=None)
    productParser = property(get_productParser, fset=None,fdel=None,doc=None)
    
    def feed(self, data) -> list:
        # si aucun nouveau produit n a ete reconnu => sortir de l analyse
        total = len(self.__productsIdTotal)
        self.__productsId = []
        super().feed(data)
        current = len(self.__productsId)
        print('nb de produits apres analyse:',total, ' (+ ', current , ')')
        return self.__productsId

    #implements parsing methods
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
            #print(attrs)
            if( attrs[0][0] == 'href') and attrs[1][0] == 'title':
                url = attrs[0][1]
                name = attrs[1][1]
                if( self.__productsIdTotal.get(name) == None):
                    pid = ProductId(URL=url, Nom=name)
                    self.__productsId.append(pid)
                    self.__productsIdTotal[name] = pid
                    self.__numberOfProducts = self.__numberOfProducts + 1

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__analysed > 0 and tag == 'ul':
            self.__analysed = self.__analysed - 1

def _webanalyseIndexedURL(instanceParser, URLName) -> list:
    """ return yield list if the url is providing new data """
    """retry some times if no new data is provided"""
    i = 0
    retry = 2 # si 2 pages sont identiques, faire un increment de l index pour le nb de retry
    while True:
        url = URLName.format(i)
        print(url)
        p = _webanalyseURL(instanceParser, url)
        if p == None or len(p) == 0:
            if(retry == 0):
                break
            else:
                retry = retry - 1
        else:
            i = i + 1
            for n in p:
                yield n
    return None


def _webanalyseURL(instanceParser, url) -> list:
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
        return instanceParser.feed(html)


#Main inputs
# URL Liste

InputsList2 = [('IndexURL__',BricoflorProductListHTMLParser(),'https://www.bricoflor.fr/sol/moquette.html?p={}'),
              ('FixedURL',EspaceRevetementProductListHTMLParser(),'https://www.espacerevetements.com/index.php?id_category=17&controller=category'),
              ('OffsetURL',LeroyMerlinProductListHTMLParser(),'https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?resultOffset={0}&resultLimit={99}&resultListShape=MOSAIC&priceStyle=SALEUNIT_PRICE')]

InputsList = [ BricoflorProductListHTMLParser('https://www.bricoflor.fr/sol/moquette.html?p={}') ]
#            EspaceRevetementProductListHTMLParser('https://www.espacerevetements.com/index.php?id_category=17&controller=category'),
#            LeroyMerlinProductListHTMLParser('https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?resultOffset={0}&resultLimit={99}&resultListShape=MOSAIC&priceStyle=SALEUNIT_PRICE')]


productsList = list()
numberOfProduct = 0


for parser in InputsList:
    print (parser)
    for product in parser.productsList:
        print(product)
        numberOfProduct = numberOfProduct + 1
        productsList.append(product)
print('NumberOfProduct',numberOfProduct) 

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