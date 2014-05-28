__author__ = 'cneylon'
from oacensus.commands import defaults
from oacensus.models import Article
from oacensus.scraper import Scraper
from oacensus.models import Repository
from oacensus.models import Instance
from tests.utils import setup_db
setup_db()

test_doi_open = '10.1371/journal.pone.0001164'
test_doi_embargoed = '10.1007/s00024-004-0394-3'
test_doi_closed = '10.1063/1.3663569'
test_doi_restricted = '10.1111/j.1365-2125.2009.03481.x'

# This is a DOI from the Crossref Labs 'Journal of Pyschoceramics' which should never appear in OpenAIRE
test_doi_no_response = '10.5555/12345678'

def test_openaire_scraper():
    dois = [
      test_doi_open,
      test_doi_embargoed,
      test_doi_closed,
      test_doi_restricted,
      test_doi_no_response
    ]

    doilist = Scraper.create_instance("doilist")
    doilist.update_settings({"doi-list" : dois })
    doilist.run()

    # Test cases #
    ##############
    # Does the scraper run properly?
    # Are the relevant repositories created?
    # Are all DOIs that should be returned?
    # TODO: Do all returned DOIs provide the 'correct' answer?

    # Scraper runs successfully
    scraper = Scraper.create_instance("openaire")
    scraper.run()

    # Repositories created properly
    r1 = Repository.select()
    repos = [r for r in r1]
    assert len(repos) > 3

    names = [r.name for r in r1]
    assert 'Oxford University Research Archive' in names
    assert 'Europe PubMed Central' in names
    assert 'Surrey Research Insight' in names
    assert 'DSpace at VSB Technical University of Ostrava' in names

    # All appropriate DOI's returned
    for d in dois[0:4]:
        a = Article.select().where(Article.doi == d)[0]
        instances = [inst for inst in a.instances]
        assert len(instances) > 0
        for inst in instances:
            assert inst.free_to_read is not None

    # Nonexistent doi not returned
    a = Article.select().where(Article.doi == test_doi_no_response)[0]
    instances = [inst for inst in a.instances]
    assert len(instances) == 0

    # Test correct answer for 'open' case
    a = Article.select().where(Article.doi == test_doi_open)[0]
    instances = [inst for inst in a.instances]
    for inst in instances:
        assert inst.free_to_read

    # Test correct answer for non-open cases
    for doi in [test_doi_restricted, test_doi_closed, test_doi_embargoed]:
        a = Article.select().where(Article.doi == doi)[0]
        instances = [inst for inst in a.instances]
        for inst in instances:
            print inst.repository.name, inst.free_to_read
            assert not inst.free_to_read




