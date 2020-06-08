
# https://www.programiz.com/python-programming/
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import abc
import collections
from dataclasses import dataclass, asdict

#Product = collections.namedtuple(
#    'Produit', 'URL Nom Poids Epaisseur Couleur Isolation Prix', defaults=(None,) * 7)
#ProductId = collections.namedtuple('IdProduit', 'URL Nom')

#Product = collections.namedtuple(
#    'Produit', 'URL Nom Contenu Longueur Complet', defaults=(None,) * 5)
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


###############################
# CLASS DEFINITION
# URLHTML Parser for providing several config using index inside URL
# PRODUCTS LIST HTML PARSER for parsing an URL containing a PRODUCT LIST
# PRODUCT HTML PARSER for parsing an
###############################
class URLHTMLParser(HTMLParser):
    __metaclass__ = abc.ABCMeta

    __headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language':'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    @abc.abstractmethod
    def _webanalyse(self, url) -> list:
        pass 

    def _webanalyseURL(self, url) -> list:
        """ return list if the url is providing a collection or just one product """
        req = Request(url, headers=self.__headers)
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

    def _webanalyseIndexedURL(self, URLName, begin = 0) -> list:
        return self._webanalyseSlotURL(URLName,begin,1)

    def _webanalyseEndedIndexedURL(self, URLName, URLExtension, begin, end) -> list:
        """ return yield list if the url is providing new data """
         # il existe plusieurs pages de produits allant de URLName à URLName?p=2 jusqu'à end
        p = list()
        for id in range(begin,end+1) :
            if( id == begin ):
                url = URLName
            else:
                url = URLName + URLExtension + str(id)
            #print trace / not debug
            print(url)
            p.extend(self._webanalyseURL(url))
        return p

    def _webanalyseSlotURL(self, URLName, begin = 0 , offset = 1) -> list:
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
        self.__completed = False

    @abc.abstractmethod
    def _analyseRaw(self, data):
        self.__completed = True 

    def setCompleted(self, flag = True):
        self.__completed = flag

    def set_product(self, id):
        self.__product = asdict(id)

    def get_product(self) -> dict:
        return self.__product

    def set_productData(self, key, data):
        self.__product[key] = data        

    product = property(fget=get_product, fset=set_product, fdel=None, doc=None)

    def feed(self, data) -> dict:
        self.__completed = False
        try:            
            super().feed(data)
        except (AttributeError, IndexError, ValueError, UnicodeDecodeError) as e:
            print(e)
        
        if not self.__completed:
            #stream flow analysis if needed
            self._analyseRaw(data)
            super().reset()

        return self.__product


class ProductsListHTMLParser(URLHTMLParser):

    def __init__(self, productListUrl=None):
        super().__init__()
        self.__productsId = None
        self.__productsIdTotal = {}
        self.__URL = productListUrl
        self.__productParser = None
    
    def get_URL(self):
        return self.__URL

    def get_productParser(self):
        return self.__productParser

    def set_productParser(self, productparser):
        self.__productParser = productparser

    def appendProduct(self, pid):
        if(self.__productsIdTotal.get(pid.URL) == None):
            self.__productsId.append(pid)
            self.__productsIdTotal[pid.URL] = pid

    def get_products(self) -> list:
        # for each product id (url)
        for pid in self._webanalyse(self.URL):
            # analyse the product thx to its id
            self.productParser.set_product(pid)
            for p in self.productParser._webanalyseURL(pid.URL):
                yield p

    URL  = property(get_URL, fset=None, fdel=None, doc=None)
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

