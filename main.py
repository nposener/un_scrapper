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
            for symbol in symbols:
                print('{}) Searching: {} in {}'.format(i + 1, searchterm, symbol['symbol']))
                session = Session(url)
                session.searchDoc(symbol['symbol'], searchterm)
                for result in session.readResults(symbol['filter']):
                    if not len(result) == 0:
                        with open ('output.csv','a') as f:
                            f.write('{},{},{},{}\n'.format(searchterm, symbol['symbol'], result['text'] ,result['link']))
                    else:
                        with open ('output.csv','a') as f:
                            f.write('{},No resualts in {}\n'.format(searchterm, symbol['symbol']))
                session.driver.close()

def killBrowser():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options, executable_path='./geckodriver.exe')
    driver.quit()
    print('killed {}'.format(driver))

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
    with open('output.csv', 'w') as f:
        f.write('SearchTerm,Symbol,DocName,DocLink\n')

    searchAndWrite(searchterms, symbols, url)


if __name__ == '__main__':
    main()

