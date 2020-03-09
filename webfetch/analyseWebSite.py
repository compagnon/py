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

###############################
## CLASS DEFINITION
## HTML PARSER
###############################

class BricoflorProductListHTMLParser(HTMLParser):
    """Parser Class pour Bricoflor"""
    analysed = 0

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        if self.analysed == 0 and tag == 'ul':
            #print("Encountered a start tag:", tag, attrs)
            for attribute in attrs:
                    if attribute[0] == 'class' and attribute[1] == 'products-grid row large-products-grid':
                        self.analysed = self.analysed + 1
                        print(attribute[1])
        elif self.analysed > 0 and tag == 'ul':
            self.analysed = self.analysed + 1
        elif self.analysed and tag == 'a':
            print(attrs)

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        if self.analysed > 0 and tag == 'ul':
            self.analysed = self.analysed - 1

###############################
#    def handle_data(self, data):
#        print("Encountered some data  :", data)

#    def handle_data(self, data):
#        print("Encountered some data  :", data)

def manageIndexURL(instanceParser, URLName):
    """gestion d une URL avec un index allant de 0  à tant qu'une page existe"""
    i = 0
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
            # everything is fine
            html = response.read().decode('utf-8')
            instanceParser.feed(html)
            i = i + 1

#Main inputs
# URL Liste

InputsList = [('IndexURL',BricoflorProductListHTMLParser(),'https://www.bricoflor.fr/sol/moquette.html?p={}'),
              ('FixedURL','EspaceRevetementProductListHTMLParser','https://www.espacerevetements.com/index.php?id_category=17&controller=category'),
              ('OffsetURL','LeroyMerlinProductListHTMLParser','https://www.leroymerlin.fr/v3/p/produits/carrelage-parquet-sol-souple/moquette-jonc-de-mer-et-sisal/moquette-de-sol-en-rouleau-l1308217073?resultOffset={0}&resultLimit={99}&resultListShape=MOSAIC&priceStyle=SALEUNIT_PRICE')]


for configType in InputsList:
    print (configType[0])
    if configType[0] == 'IndexURL':
        manageIndexURL(configType[1],configType[2])
    elif configType[0] == 'FixedURL':
        pass
    elif configType[0] == 'OffsetURL':
        pass