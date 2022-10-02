import os

import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        self.source = None
        self.soup = None

    @staticmethod
    def checkFile(file):
        return os.path.isfile(file)

    @staticmethod
    def getSourceSoup(url):
        source = requests.get(url)
        soup = BeautifulSoup(
            source.text, 'html.parser')
        return source, soup

    @staticmethod
    def getAllElements(soup, elementType, attr):
        return soup.find_all(elementType, attr)

    @staticmethod
    def getElement(soup, elementType, attr):
        return soup.find(elementType, attr)