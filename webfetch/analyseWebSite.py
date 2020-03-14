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
Product = collections.namedtuple('Produit', 'URL Nom Poids Epaisseur Isolation Prix', defaults=(None,) * 6)
ProductId = collections.namedtuple('IdProduit', 'URL Nom')

###############################
## CLASS DEFINITION
## HTML PARSER
###############################
class LeroyMerlinProductListHTMLParser(HTMLParser):
    pass

class EspaceRevetementProductListHTMLParser(HTMLParser):
    pass

class BricoflorProductHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.__analysed = False
        self.__datafield = False
        self.__field = None
        self.__product = dict()
        self.__productTuple = None
        self.__productIdTuple =None

    def get_product(self) -> Product:
        return self.__productTuple

    def set_productId(self,id):
        self.__productIdTuple = id       

    def get_productId(self):
        return self.__productIdTuple

    product = property(get_product, fset=None,fdel=None,doc=None)
    productId = property(get_productId, fset=set_productId,fdel=None,doc=None)

    def feed(self, data) -> int:
        if self.__productIdTuple != None:
            self.__product = self.__productIdTuple._asdict()
        super().feed(data)
        self.__productTuple = Product(**self.__product)
        print('Produit:',self.__productTuple)
        self.__product.clear()
        self.__productIdTuple == None
        return 1
        
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
    def __init__(self):
        super().__init__()
        self.__analysed = 0
        self.__numberOfProducts = 0
        self.__productsId = {}
        self.__productPageParser = BricoflorProductHTMLParser()

    def get_productParser(self):
        return self.__productPageParser

    def get_productsIdList(self) -> list:
        return self.__productsId.values()

    productsIdList = property(get_productsIdList, fset=None,fdel=None,doc=None)
    productParser = property(get_productParser, fset=None,fdel=None,doc=None)
    
    def feed(self, data) -> int:
        # si aucun nouveau produit n a ete reconnu => sortir de l analyse
        previous = self.__numberOfProducts
        super().feed(data)
        print('nb de produits apres analyse:',self.__numberOfProducts)
        return self.__numberOfProducts - previous

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
                if( self.__productsId.get(name) == None):
                    self.__productsId[name] = ProductId(URL=url, Nom=name)
                    self.__numberOfProducts = self.__numberOfProducts + 1

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__analysed > 0 and tag == 'ul':
            self.__analysed = self.__analysed - 1


def webanalyseIndexedURL(instanceParser, URLName) -> bool:
    """ return true if the url is providing new data """
    """gestion d une URL avec un index allant de 0  à tant qu'une page existe"""
    i = 0
    retry = 2 # si 2 pages sont identiques, faire un increment de l index pour le nb de retry
    newDataFlag = False
    while True:
        url = URLName.format(i)
        print(url)
        if (webanalyseURL(instanceParser, url)):
            newDataFlag = True
        elif(retry == 0):
            break
        else:
            retry = retry - 1
        i = i + 1
    return newDataFlag


def webanalyseURL(instanceParser, url) -> bool:
    """ return true if the url is providing new data """
    req = Request(url)
    try:
        response = urlopen(req)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
        return False
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
        return False
    else:
        # la page existe, analyser la page avec un Parseur HTML
        html = response.read().decode('utf-8')
        return instanceParser.feed(html) != 0


#Main inputs
# URL Liste

InputsList = [('IndexURL',BricoflorProductListHTMLParser(),'https://www.bricoflor.fr/sol/moquette.html?p={}'),
              ('FixedURL',EspaceRevetementProductListHTMLParser(),'https://www.espacerevetements.com/index.php?id_category=17&controller=category'),
              ('OffsetURL',LeroyMerlinProductListHTMLParser(),'https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?resultOffset={0}&resultLimit={99}&resultListShape=MOSAIC&priceStyle=SALEUNIT_PRICE')]

productsList = list()

for configType in InputsList:
    print (configType[0])
    if configType[0] == 'IndexURL':
        if webanalyseIndexedURL(configType[1],configType[2]):
            #print(configType[1].productsIdList)
            numberOfProduct = 0
            for productId in configType[1].productsIdList:
#                productId = ProductId(URL='https://www.bricoflor.fr/vorwerk-safira-8h76.html', Nom='Vorwerk Safira "8H74"')
#                print("Analyse Produit",productId)
                configType[1].productParser.productId = productId
                if webanalyseURL(configType[1].productParser,productId.URL) :
                    numberOfProduct = numberOfProduct + 1
                    print(configType[1].productParser.product)
        print('NnumberOfProduct',numberOfProduct)

    elif configType[0] == 'FixedURL':
        pass
    elif configType[0] == 'OffsetURL':
        pass