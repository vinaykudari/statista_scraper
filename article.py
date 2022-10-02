import os
import requests

from helper import Scraper


class Article(Scraper):
    def __init__(self, url, mediaPath='data/media', dataPath='data'):
        super().__init__()
        self.graphicPath = None
        assert url != '', 'invalid url'
        
        self.url = url
        self.dataPath = f'{os.getcwd()}/{dataPath}'
        self.mediaPath = f'{os.getcwd()}/{mediaPath}' 
        self.title = ''
        self.body = ''
        self.tag = ''
        self.publishedDate = ''
        self.articleId = None
        self.graphicUrl = None
        
        self.bootstrap()
        
    def bootstrap(self):
        self.source, self.soup = self.getSourceSoup(self.url)
        self.setArticleId()
        self.setTitle()
        self.setBody()
        self.setTag()
        self.setPublishedDate()
        self.graphicPath = f'{self.mediaPath}/{self.articleId}.jpeg'
        self.setGraphic()
            
    def setArticleId(self):
        lis = self.url.split('/') 
        self.articleId = lis[4]
    
    def setTitle(self):
        element = self.getElement(
            self.soup,
            'h1', {'id' : 'infographicArticleTitle'}
        )
        if element:
            self.title = element.getText().strip()
            
    def setBody(self):
        element = self.getElement(
            self.soup,
            'div', {'class': 'article__contentText'}
        )
        if element:
            self.body = element.getText().strip()
            
    def setTag(self):
        element = self.getElement(
            self.soup,
            'div', {'class': 'article__topic'}
        )
        if element:
            self.tag = element.getText().strip()
            
    def setPublishedDate(self):
        element = self.getElement(
            self.soup,
            'time', {'class': 'infographic__date--published'}
        )
        if element:
            self.publishedDate = element.attrs.get('datetime', '').strip()
            
    def setGraphicUrl(self):
        element = self.getElement(
            self.soup,
            'div', {'class': 'article__graphic'}
        )
        if element:
            self.graphicUrl = element.find('img').attrs.get('data-src', '')
            
    def checkMedia(self):
        return self.checkFile(self.graphicPath)
        
    def setGraphic(self):
        if not self.graphicUrl:
            self.setGraphicUrl()
            
            if not self.checkMedia():
                data = requests.get(self.graphicUrl).content

                os.makedirs(os.path.dirname(self.graphicPath), exist_ok=True)
                with open(self.graphicPath, 'wb') as handler:
                    handler.write(data)
                
    def serialize(self):
        mp = {
            'title': self.title, 
            'body': self.body,
            'graphic': self.graphicPath,
            'publishedDate': self.publishedDate,
            'tag': self.tag,
        }
        
        return self.articleId, mp
        