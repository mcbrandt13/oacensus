__author__ = 'cneylon'

from oacensus.commands import defaults
from oacensus.scraper import Scraper
import oacensus.reports.pubspeed_excel as Report
from tests.utils import setup_db
setup_db()

JOURNALS = ["Journal of virology",
            "Current Biology : CB",
            "Nature Neuroscience",
            "Proceedings of the National Academy of Sciences of the United States of America",
            "Genes & development",
            "Bioinformatics",
            "Cell",
            "Science (New York, N.Y.)",
            "Cell host & microbe",
            "Nature genetics",
            "Molecular systems biology",
            "Nature",
            "PLoS neglected tropical diseases",
            "The Journal of infectious diseases",
            "Nature medicine",
            "Genome research",
            "BMC infectious diseases",
            "PLoS genetics",
            "BMC public health",
            "Nature cell biology",
            "The American journal of tropical medicine and hygiene",
            "PeerJ",
            "SpringerPlus",
            "BMJ open",
            "eLife",
            "Nature communications",
            "Scientific reports"]

search_term = "(" + " OR ".join(['("%s"[Journal])' % title for title in JOURNALS]) + ")"
search_date_string = ' AND ("2013-01-01"[Date - Publication] : "2013-01-10"[Date - Publication])'

scraper = Scraper.create_instance('pubmed')
scraper.update_settings({'search' : search_term + search_date_string,
                          'start-period' : '2013-01',
                          'end-period' : '2013-01'})
scraper.run()

crossref = Scraper.create_instance('crossref')
crossref.run()

doaj = Scraper.create_instance('doaj')
doaj.run()

report = Report.PubspeedExcel()
report.initialize_settings()
report.run()



