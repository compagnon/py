## analyse du site Bricoflor

url='https://www.bricoflor.fr/sol/moquette.html'

#https://www.bricoflor.fr/sol/moquette.html?p=2

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser



class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        global analyse
        # print("Encountered a start tag:", tag)
        if analyse == 0 and tag == 'ul':
            #print("Encountered a start tag:", tag, attrs)
            for attribute in attrs:
                    if attribute[0] == 'class' and attribute[1] == 'products-grid row large-products-grid':
                        analyse = analyse + 1
                        print(attribute[1])
        elif analyse > 0 and tag == 'ul':
            analyse = analyse + 1
        elif analyse and tag == 'a':
            print(attrs)

    def handle_endtag(self, tag):
        global analyse
        # print("Encountered an end tag :", tag)
        if analyse > 0 and tag == 'ul':
            analyse = analyse - 1


#    def handle_data(self, data):
#        print("Encountered some data  :", data)

#    def handle_data(self, data):
#        print("Encountered some data  :", data)



req = Request(url)
try:
    response = urlopen(req)
except HTTPError as e:
    print('The server couldn\'t fulfill the request.')
    print('Error code: ', e.code)
except URLError as e:
    print('We failed to reach a server.')
    print('Reason: ', e.reason)
else:
    # everything is fine
    html = response.read().decode('utf-8')
    analyse=0
    parser = MyHTMLParser()
    
    parser.feed(html)