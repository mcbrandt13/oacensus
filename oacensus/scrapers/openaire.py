__author__ = 'cneylon'
from oacensus.scraper import ArticleScraper
from oacensus.models import Article
from oacensus.models import Repository
from oacensus.models import Instance
import json
import requests
import xml.etree.ElementTree as ET

class OpenAIRE(ArticleScraper):
    """
    Gets accessibility information for articles with DOIs in the database.
    """
    aliases = ['openaire']

    _settings = {
            'base-url' : ("Base url of OpenAIRE API", "http://api.openaire.eu/search/publications"),
            }

    def scrape(self):
        # don't use scrape method since our query depends on db state, so
        # caching will not be accurate
        pass

    def process(self):
        articles = Article.select().where(~(Article.doi >> None))
        for article in articles:
            response = requests.get(self.setting('base-url'), params = {'doi' : article.doi})
            openaire_response = ET.fromstring(response.text.encode('utf-8'))

            for inst in openaire_response.iter('instance'):
                reponame = inst.find('hostedby').get('name')
                repository = Repository.find_or_create_by_name({'name':reponame,
                                                                'source': 'openaire',
                                                                'log' : 'Created by openaire plugin'})


                status = inst.find('licence').get('classname')
                ftr = {'Open Access' : True,
                       'Closed Access' : False,
                       'Embargo' : False,
                       'Restricted' : False}.get(status, False)

                url = inst.find('webresource').find('url').text
                Instance.create(article = article,
                                repository = repository,
                                free_to_read = ftr,
                                info_url=url,
                                source=self.db_source(),
                                log='OpenAIRE response obtained from %s repository' % reponame)