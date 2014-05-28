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
        articles = Article.select()
        for [article in articles if article.doi]:
            response = requests.post(self.setting('base-url'), data = json.dumps(article.doi))
            openaire_response = ET.fromstring(response.text)

            instances = openaire_response.iterfind('instance')
            for inst in instances if instances:
                reponame = inst.find('hostedby').get('name')
                status = inst.find('license').get('classname')
                ftr = {'Open Access' : True,
                       'Closed Access' : False,
                       'Embargo' : False,
                       'Restricted' : False}.get(status, False)

                url = inst.find('webresource').find('url').text
                Instance.create(article=article
                                repository=self.create_or_return_repository(reponame),
                                free_to_read = ftr,
                                info_url=url,
                                source=self.db_source(),
                                log=self.db_source())

    def create_or_return_repository(self, reponame):
        repo = Repository.select().where(Repository.name == reponame)
        if repo:
            return repo
        else:
            Repository.create(name = reponame)