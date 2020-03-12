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
Product = collections.namedtuple('Produit', 'URL Nom Poids Epaisseur Isolation', defaults=(None,) * 5)

###############################
## CLASS DEFINITION
## HTML PARSER
###############################
class LeroyMerlinProductListHTMLParser(HTMLParser):
    pass

class EspaceRevetementProductListHTMLParser(HTMLParser):
    pass

class BricoflorProductListHTMLParser(HTMLParser):
    """Parser Class pour Bricoflor"""
    # instance attribute

    __analysed = 0
    __products = {}

    def get_productsList(self):
        return self.__products

    productsList = property(get_productsList, fset=None,fdel=None,doc=None)
    
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
                if( self.__products.get(name) == None):
                    self.__products[name] = Product(URL=url, Nom=name)

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.__analysed > 0 and tag == 'ul':
            self.__analysed = self.__analysed - 1

###############################
#    def handle_data(self, data):
#        print("Encountered some data  :", data)

#    def handle_data(self, data):
#        print("Encountered some data  :", data)

def manageIndexURL(instanceParser, URLName):
    """gestion d une URL avec un index allant de 0  à tant qu'une page existe"""
    i = 1
    productsNumber_previous = 0
    while True:
        url = URLName.format(i)
        print(url)
        req = Request(url)
        try:
            response = urlopen(req)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            break
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
            break
        else:
            # la page existe
            html = response.read().decode('utf-8')
            instanceParser.feed(html)

            productsNumber_current = len(instanceParser.productsList.keys())
            # si aucun nouveau produit n a ete reconnu => sortir de l analyse
            if(productsNumber_previous == productsNumber_current):
                break
            
            i = i + 1            
            productsNumber_previous = productsNumber_current

#Main inputs
# URL Liste

InputsList = [('IndexURL',BricoflorProductListHTMLParser(),'https://www.bricoflor.fr/sol/moquette.html?p={}'),
              ('FixedURL',EspaceRevetementProductListHTMLParser(),'https://www.espacerevetements.com/index.php?id_category=17&controller=category'),
              ('OffsetURL',LeroyMerlinProductListHTMLParser(),'https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?resultOffset={0}&resultLimit={99}&resultListShape=MOSAIC&priceStyle=SALEUNIT_PRICE')]


for configType in InputsList:
    print (configType[0])
    if configType[0] == 'IndexURL':
        manageIndexURL(configType[1],configType[2])
        print(configType[1].productsList)
    elif configType[0] == 'FixedURL':
        pass
    elif configType[0] == 'OffsetURL':
        pass