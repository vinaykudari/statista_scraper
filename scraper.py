import json
import os
import requests

from bs4 import BeautifulSoup

STATISTA_HOME = 'https://www.statista.com'

class Scraper:
    def __init__(self):
        self.source = None
        self.soup = None
        
    @staticmethod
    def checkFile(file):
        return os.path.isfile(file)
    
    def getSourceSoup(self, url, force=False):
        source = requests.get(url)
        soup = BeautifulSoup(
            source.text, 'html.parser')
        return source, soup
    
    def getAllElements(self, soup, elementType, attr):
        return soup.find_all(elementType, attr)
            
    def getElement(self, soup, elementType, attr):
        return soup.find(elementType, attr)
    

class Statista(Scraper):
    ''' Scrape chart of the day infographics'''
    def __init__(self, dataPath='data'):
        super().__init__()
        self.url = self.getPageUrl()
        self.dataPath = f'{os.getcwd()}/{dataPath}'
        self.mediaPath = f'{dataPath}/media'
        self.dataFilePath = f'{dataPath}/info.json'
        self.infoFileDesc = None
        
    @staticmethod
    def scrapeArticle(articleUrl):
        page = Article(articleUrl)
        articleId, article =  page.serialize()
        return articleId, article
        
    def getPageUrl(self, path='chartoftheday', page=1):
        return f'{STATISTA_HOME}/{path}/ALL/p/{page}/'
    
    def getGraphicPath(self, articleId):
        return f'{self.mediaPath}/{articleId}.jpeg'
    
    def isValidPage(self, soup):
        return self.getElement(
            soup, 'div', {'class' : 'note'}) != None
    
    def getInfoFileDesc(self):
        if not self.infoFileDesc or self.infoFileDesc.closed:
            self.infoFileDesc = open(f'{self.dataPath}/info.json', 'w+')
        return self.infoFileDesc
    
    def getArticleUrls(self, pageNo):
        lis = []
        pageUrl = self.getPageUrl(page=pageNo)
        source, soup = self.getSourceSoup(pageUrl)
        articles = self.getAllElements(
            soup, 'a', {'class' : 'infographicsPanelCard'})
        
        for article in articles:
            articleUrl = article.attrs.get('href', None)
            if not articleUrl:
                continue
                
            articleId = articleUrl.split('/')[2]
            graphicFile = self.checkFile(
                self.getGraphicPath(articleId))
            textFile = self.checkFile(self.dataFilePath)
            
            if not graphicFile or not textFile:
                lis.append(f'{STATISTA_HOME}{articleUrl}')
        
        return lis
    
    def scrapeArticles(self, pageNo):
        articles = []
        articleUrls = self.getArticleUrls(pageNo)
        for articleUrl in articleUrls:
            articles.append(self.scrapeArticle(articleUrl))
        return articles
        
    def scrape(self, start=1, end=124):
        for pageNo in range(start, end+1):
            articles = self.scrapeArticles(pageNo)
            
            try:
                with open(f'{self.dataPath}/info.json', 'r') as fileDesc:
                    data = fileDesc.read()
            except Exception as e:
                data = {}
                
            if not data:
                obj = {}
            else:
                obj = json.loads(data)

            for (articleId, article) in articles:
                obj[articleId] = article
                    
            with open(f'{self.dataPath}/info.json', 'w+') as fileDesc:
                json.dump(obj, fileDesc)
                
        self.articles = obj