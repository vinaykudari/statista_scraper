import json
import os
import time

from article import Article
from helper import Scraper

STATISTA_HOME = 'https://www.statista.com'


class Statista(Scraper):
    """ Scrape chart of the day infographics"""

    def __init__(self, dataPath='data'):
        super().__init__()
        self.articles = None
        self.url = self.getPageUrl()
        self.dataPath = f'{os.getcwd()}/{dataPath}'
        self.mediaPath = f'{dataPath}/media'
        self.dataFilePath = f'{dataPath}/info.json'
        self.infoFileDesc = None

    @staticmethod
    def scrapeArticle(articleUrl):
        page = Article(articleUrl)
        articleId, article = page.serialize()
        return articleId, article

    @staticmethod
    def getPageUrl(path='chartoftheday', page=1):
        return f'{STATISTA_HOME}/{path}/ALL/p/{page}/'

    def getGraphicPath(self, articleId):
        return f'{self.mediaPath}/{articleId}.jpeg'

    def isValidPage(self, soup):
        return self.getElement(
            soup, 'div', {'class': 'note'}) is not None

    def getInfoFileDesc(self):
        if not self.infoFileDesc or self.infoFileDesc.closed:
            self.infoFileDesc = open(f'{self.dataPath}/info.json', 'w+')
        return self.infoFileDesc

    def getArticleUrls(self, pageNo):
        lis = []
        alreadyPresent = 0
        pageUrl = self.getPageUrl(page=pageNo)
        source, soup = self.getSourceSoup(pageUrl)
        articles = self.getAllElements(
            soup, 'a', {'class': 'infographicsPanelCard'})

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
            else:
                alreadyPresent += 1

        return lis, alreadyPresent

    def scrapeArticles(self, pageNo):
        articles = []
        article = None
        articleUrls, alreadyPresent = self.getArticleUrls(pageNo)
        for articleUrl in articleUrls:
            try:
                article = self.scrapeArticle(articleUrl)
            except Exception as e:
                print(f'Exception for {articleUrl}; e = {e}')
            if article:
                articles.append(article)
        return articles, alreadyPresent

    def scrape(self, start=1, end=124):
        for pageNo in range(start, end + 1):
            articles, alreadyPresent = self.scrapeArticles(pageNo)
            print(f'Page: {pageNo}, New: {len(articles)}, Already Present: {alreadyPresent}')
            obj = {}
            try:
                with open(f'{self.dataPath}/info.json', 'r') as fileDesc:
                    data = fileDesc.read()
            except Exception as e:
                data = {}

            if data:
                obj = json.loads(data)

            for (articleId, article) in articles:
                obj[articleId] = article

            with open(f'{self.dataPath}/info.json', 'w+') as fileDesc:
                json.dump(obj, fileDesc)

            self.articles = obj

        time.sleep(10)
