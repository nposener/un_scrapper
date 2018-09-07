from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import atexit

class Session(object):
    def __init__(self, url):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(firefox_options=options, executable_path='./geckodriver.exe')
        self.driver.get(url)

    def searchDoc(self, symbol, text):
        symbol_field = self.driver.find_element_by_id('view:_id1:_id2:txtSymbol')
        text_field = self.driver.find_element_by_id('view:_id1:_id2:txtFTSrch')
        search_button = self.driver.find_element_by_id('view:_id1:_id2:btnRefine')
        symbol_field.send_keys(symbol)
        text_field.send_keys(text)
        search_button.click()

    def readResults(self, filter):
        wait = WebDriverWait (self.driver, 600)
        wait.until(EC.presence_of_element_located((By.ID,'view:_id1:_id2:cbMain:_id135:cfPageTitle')))
        results = self.driver.find_elements_by_xpath("//a[contains(@id, 'linkURL')]")
        filteredResults = []
        for result in results:
            if filter in result.text.lower():
                filteredResults.append({'text':result.text,'link':result.get_property('href')})
        return filteredResults

def searchAndWrite(searchterms, symbols, url):
    for i, searchterm in enumerate(searchterms):
        if not searchterm == '':
            with open('webpage\\index.html', 'a') as html:
                html.write('''<h3 class='card-title'>{}</h3>
                <table class="table table-sm">
				<thead><th scope='col'>SYMBOL</th><th scope='col'>DOC NAME</th><th scope='col'>DOC LINK</th></thead>
				<tbody>
                '''.format(searchterm))
            for symbol in symbols:
                print('{}) Searching: {} in {}'.format(i + 1, searchterm, symbol['symbol']))
                session = Session(url)
                session.searchDoc(symbol['symbol'], searchterm)
                if not session.readResults(symbol['filter']) == 0:
                    for result in session.readResults(symbol['filter']):
                        writeResult(symbol['symbol'], result['text'] ,result['link'])
                else:
                        writeResult(symbol['symbol'], '<b>NO RESULTS<b>','')
                session.driver.close()
            with open('webpage\\index.html', 'a') as html:
                html.write('</tbody></table>\n')

def writeResult(symbol, docName, docLink):
    with open ('webpage\\index.html', 'a') as html:
        html.write('<tr><td>{}</td><td>{}</td><td><a href={}><i>LINK</i></a></td></tr>\n'.format(symbol,docName,docLink))

def killBrowser():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options, executable_path='./geckodriver.exe')
    driver.quit()
    print('killed {}'.format(driver))

def createHTMLhead():
    with open ('webpage\\index.html', 'w') as html:
        html.write('''
        <!doctype html>
        <html lang="en">
        <head>
        <title>UN Scraper results</title>
        <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
	    </head>
        <body class='card w-75'>
	        <div class='container'><h2> Results </h2><div class='card-body'>
        ''')

def closeHTML():
    with open ('index.html', 'a') as html:
        html.write('</div></div></body></html>')

def main():
    symbols = [
        {'symbol':'a*251', 'filter':'251'},
        {'symbol': 'a/bur/*1', 'filter': 'bur'}
    ]
    url = 'https://documents.un.org/prod/ods.nsf/home.xsp'
    with open ('./SearchTerms.csv', 'r') as f:
        searchterms = f.read().split('\n')
    print(searchterms)
    atexit.register(killBrowser)
    atexit.register(closeHTML)
    createHTMLhead()
    searchAndWrite(searchterms, symbols, url)


if __name__ == '__main__':
    main()

