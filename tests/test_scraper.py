from datetime import datetime
from dateutil import relativedelta
from oacensus.commands import defaults
from oacensus.scraper import Scraper
from tests.utils import setup_db
from oacensus.models import Publisher

setup_db()

class DummyScraper(Scraper):
    """
    Scraper which does nothing for testing scraper methods.
    """
    aliases = ['dummyscraper']

    def scrape(self):
        pass

    def process(self):
        pass

def test_hashcode():
    scraper = Scraper.create_instance('dummyscraper', defaults)
    assert len(scraper.hashcode(scraper.hash_settings())) == 32

def test_run():
    scraper = Scraper.create_instance('dummyscraper', defaults)
    scraper.run()

def make_article_scraper(overrides = None):
    scraper = Scraper.create_instance('articlescraper', defaults)
    settings = {"start-period" : "2010-01", "end-period" : "2010-12"}
    if overrides:
        settings.update(overrides)
    scraper.update_settings(settings)
    return scraper

def test_no_end_month_is_ok():
    scraper = make_article_scraper({
        "end-period" : None
        })

    periods = [p for p in scraper.start_dates()]
    assert periods[-1] < datetime.now()
    assert periods[-1] > datetime.now() + relativedelta.relativedelta(months = -2)

def test_invalid_end_month_before_start_month():
    scraper = make_article_scraper({
        "end-period" : "2009-12"
        })

    try:
        scraper.start_dates()
        assert False, "should not be here"
    except Exception as e:
        assert "must be before" in str(e)

def test_invalid_end_month_after_today():
    this_month = datetime.today().strftime("%Y-%m")
    scraper = make_article_scraper({
        "end-period" : this_month
        })

    try:
        scraper.start_dates()
        assert False, "should not be here"
    except Exception as e:
        assert "before the current date" in str(e)

def test_article_scraper_recurrences():
    scraper = make_article_scraper()
    periods = [p for p in scraper.start_dates()]
    assert len(periods) == 12
    assert periods[0] == datetime(2010,1,1)
    assert periods[11] == datetime(2010,12,1)

def test_article_scraper_period_hashes():
    scraper = make_article_scraper()
    for period in scraper.start_dates():
        hash_settings = scraper.period_hash_settings(period)
        assert hash_settings['period'].startswith("2010-")
        assert len(scraper.period_hashcode(period)) == 32

def test_article_scraper_periods():
    scraper = make_article_scraper()
    for start_month, end_month in scraper.periods():
        assert end_month > start_month
        assert relativedelta.relativedelta(end_month, start_month).months == 1

class ScraperWithParseException(Scraper):
    """
    A scraper which generates an exception halfway through parsing, when some
    data has already been written to the database.
    """
    aliases = ['parseexception']

    def scrape(self):
        pass

    def process(self):
        publisher = Publisher.create(name="A Publisher", source=self.db_source())
        assert self.is_data_stored()
        raise Exception("Stop here for the test.")

def test_scraper_has_no_data_stored_after_exception():
    scraper = Scraper.create_instance('parseexception', defaults)
    try:
        scraper.run()
    except Exception:
        pass
    assert not scraper.is_data_stored()
