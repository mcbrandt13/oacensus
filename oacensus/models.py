from peewee import *
from oacensus.db import db

import logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.WARN)

pubmed_external_ids = {
        'mid' : None,
        'pii' : None,
        'doi' : None,
        'oag' : {
            'name' : 'Open Article Gauge'
            },
        'nihm' : {
            'name' : "National Institutes of Health and Medicine",
            'free_to_read' : None
            },
        'pubmed' : {
            'name' : "PubMed",
            'free_to_read' : None
            },
        'pmc' : {
            'name' : "PubMed Central",
            'free_to_read' : True
            }
        }

class ModelBase(Model):
    source = CharField(help_text="Which scraper populated this information?")
    log = CharField(help_text="Messages should indicate all sources which touched this record.")

    def truncate_title(self, length=40):
        title = self.title
        if len(title) < length:
            if type(title) is str:
                return title.decode("utf-8", "ignore")
            else:
                return title
        else:
            truncated = title[0:length]
            if type(truncated) is str:
                truncated = truncated.decode("utf-8", "ignore")
            return u"{0}...".format(truncated)

    class Meta:
        database = db

    @classmethod
    def update_skip_fields(klass):
        return ('source', 'log')

    @classmethod
    def delete_all_from_source(klass, source):
        return klass.delete().where(klass.source == source).execute()

    @classmethod
    def count_from_source(klass, source):
        return klass.select().where(klass.source == source).count()

    @classmethod
    def exist_records_from_source(klass, source):
        return klass.count_from_source(source) > 0

    @classmethod
    def find_or_create_by_name(klass, args):
        name = args['name']
        try:
            return klass.get(klass.name == name)
        except klass.DoesNotExist:
            return klass.create(**args)

    @classmethod
    def update_or_create_by_name(klass, args, log_if_update):
        name = args['name']
        try:
            item = klass.get(klass.name == name)
            for k, v in args.iteritems():
                if k not in klass.update_skip_fields():
                    setattr(item, k, v)
            item.log += log_if_update
            item.save()
            return item
        except klass.DoesNotExist:
            return klass.create(**args)

    @classmethod
    def find_or_create_by_title(klass, args):
        title = args['title']
        try:
            return klass.get(klass.title == title)
        except klass.DoesNotExist:
            return klass.create(**args)

    @classmethod
    def update_or_create_by_title(klass, args, log_if_update):
        title = args['title']
        try:
            item = klass.get(klass.title == title)
            for k, v in args.iteritems():
                if k not in klass.update_skip_fields():
                    setattr(item, k, v)
            item.log += log_if_update
            item.save()
            return item
        except klass.DoesNotExist:
            return klass.create(**args)

    def __unicode__(self):
        return u"TODO IMPLEMENT UNICODE FOR %s" % self.__class__.__name__

    def __str__(self):
        return unicode(self).encode("ascii", "ignore")

class License(ModelBase):
    alias = CharField()
    title = CharField()
    url = CharField()

    def __unicode__(self):
        return u"<License {0}: {1}>".format(self.alias, self.title)

    @classmethod
    def find_license(klass, alias):
        try:
            return License.get((License.alias == alias) | (License.url == alias) | (License.title == alias))
        except License.DoesNotExist:
            return LicenseAlias.get(LicenseAlias.alias == alias).license

class LicenseAlias(ModelBase):
    license = ForeignKeyField(License)
    alias = CharField(unique=True)

class Publisher(ModelBase):
    name = CharField(index=True, unique=True)

    def __unicode__(self):
        return u"<Publisher {0}: {1}>".format(self.id, self.name)

class Journal(ModelBase):
    title = CharField(index=True,
        help_text="Name of journal.")
    url = CharField(null=True,
        help_text="Website of journal.")
    publisher = ForeignKeyField(Publisher, null=True,
        help_text="Publisher object corresponding to journal publisher.")
    issn = CharField(null=True, unique=True,
        help_text="ISSN of journal.")
    eissn = CharField(null=True,
        help_text="Electronic ISSN (EISSN) of journal.")
    doi = CharField(null=True,
        help_text="DOI for journal.")

    subject = CharField(null=True,
        help_text="Subject area which this journal deals with.")
    country = CharField(null=True,
        help_text="Country of publication for this journal.")
    language = CharField(null=True,
        help_text="Language(s) in which journal is published.")

    iso_abbreviation = CharField(null=True)
    medline_ta = CharField(null=True)
    nlm_unique_id = CharField(null=True)
    issn_linking = CharField(null=True)

    def __unicode__(self):
        return u"<Journal {0} [{1}]: {2}>".format(self.id, self.issn, self.truncate_title())

    @classmethod
    def find_or_create_by_issn(klass, args):
        issn = args['issn']
        try:
            return klass.get(klass.issn == issn)
        except klass.DoesNotExist:
            return klass.create(**args)

    @classmethod
    def update_or_create_by_issn(klass, args, log_if_update):
        issn = args['issn']
        try:
            journal = klass.get(klass.issn == issn)
            for k, v in args.iteritems():
                if k not in klass.update_skip_fields():
                    setattr(journal, k, v)
            journal.log += log_if_update
            journal.save()
        except Journal.DoesNotExist:
            journal = Journal.create(**args)

        return journal

    @classmethod
    def by_issn(cls, issn):
        try:
            return cls.get(cls.issn == issn)
        except Journal.DoesNotExist:
            pass

    def is_free_to_read(self, on_date=None):
        "Is true if there is one Rating on the journal which indicates free-to-read."
        if on_date is not None:
            raise Exception("date ranges not implemented yet")
        return any(rating.free_to_read for rating in self.ratings)

    def licenses(self):
        return [rating.license for rating in self.ratings if rating.license != None]

    def in_doaj(self):
        return self.ratings.where(Rating.source == "doaj").count() > 0

    def doaj_license(self):
        if self.in_doaj():
            license = self.ratings.where(Rating.source == "doaj")[0].license
            if license:
                return license.title

class Article(ModelBase):
    title = CharField(
        help_text="Title of article.")
    doi = CharField(null=True,
        index=True,
        help_text="Digital object identifier for article.")
    date_published = CharField(null=True,
        help_text="When article was published, in YYYY(-MM(-DD)) format.")
    date_submitted = CharField(null=True,
        help_text="When article was submitted for peer review, in YYYY(-MM(-DD)) format.")
    date_accepted = CharField(null=True,
        help_text="When article was accepted for publication, in YYYY(-MM(-DD)) format.")
    date_aheadofprint = CharField(null=True,
        help_text="Ahead of print publication date, generally AOP, in YYYY(-MM(-DD)) format.")
    period = CharField(
        help_text="Name of date-based period in which this article was scraped.")
    url = CharField(null=True,
        help_text="Web page for article information.")
    journal = ForeignKeyField(Journal, null=True,
        help_text="Journal object for journal in which article was published.")

    def __unicode__(self):
        return u'<Article {1}: {0} >'.format(self.truncate_title(), self.id)

    def instance_for(self, repository_name):
        """
        Retrieves one of this article's instances, for the provided repository name.
        """
        instances = self.instances.join(Repository).where(Repository.name == repository_name)
        if instances.count() > 0:
            return instances[0]

    def free_to_read_instances(self):
        return self.instances.select().where(Instance.free_to_read == True)

    def is_free_to_read(self):
        return self.journal.is_free_to_read() or self.free_to_read_instances().count() > 0

    def instance_licenses(self):
        return [instance.license for instance in self.instances if instance.license != None]

    def licenses(self):
        """
        Return a list of all applicable licenses.
        """
        return self.journal.licenses() + self.instance_licenses()

    def licenses_str(self):
        s = []
        for lic in self.journal.licenses():
            s.append("Journal %s license: %s" % (self.journal.title, lic))

        for lic in self.instance_licenses():
            s.append("Instance license: %s" % lic)

        return "\n".join(s)

    def ratings_str(self):
        s = []
        for ins in self.instances:
            s.append("Repository %s: %s (%s)" % (ins.repository.name, ins, ins.log))

        return "\n".join(s)

    def instances_dict(self):
        return dict((instance.repository.name, instance) for instance in self.instances)

    def instances_license_dict(self):
        return dict((instance.repository.name, instance.license) for instance in self.instances)

    def oag_license(self):
        name = pubmed_external_ids['oag']['name']
        license = self.instances_license_dict().get(name)
        if license is not None:
            return license.title

    def pmc_instance(self):
        name = pubmed_external_ids['pmc']['name']
        instance = self.instances_dict().get(name)
        if instance is not None:
            return instance

    def in_pmc(self):
        return self.pmc_instance() is not None

    def pmc_id(self):
        instance = self.pmc_instance()
        if instance is not None:
            return instance.identifier

    def license_name(self):
        licenses = self.licenses()
        if len(licenses) == 0:
            return None
        elif len(licenses) == 1:
            return licenses[0].title
        else:
            return licenses[0].title + "..."

    def license_source(self):
        # exit at first license...
        for rating in self.journal.ratings:
            if rating.license:
                return rating.source
        for instance in self.instances:
            if instance.license:
                return instance.source

    def has_license(self):
        return len(self.licenses()) > 0

    def has_open_license(self, open_licenses = None):
        article_open_licenses = [license for license in self.licenses() 
                if (open_licenses is None) or (license in open_licenses)]
        return len(article_open_licenses) > 0

    @classmethod
    def from_doi(cls, doi):
        """
        Do a case-insensitive search for DOIs.
        """
        if doi is not None:
            return Article.get((Article.doi == doi) | (Article.doi == doi.upper()))

    @classmethod
    def create_or_update_by_doi(cls, args):
        """
        If an article with DOI corresponding to the 'doi' arg exists, update
        its attributes using the remaining args. If not, create it.
        """
        try:
            article = cls.get(cls.doi == args['doi'])
            for k, v in args.iteritems():
                setattr(article, k, v)
            article.save()
        except Article.DoesNotExist:
            article = Article.create(**args)
        return article

class Repository(ModelBase):
    name = CharField(null=True,
            help_text = "Descriptive name for the repository.")
    info_url = CharField(null=True,
            help_text = "For convenience, URL of info page for the repository.")

    def __unicode__(self):
        return u'{0}'.format(self.name)

    @classmethod
    def pubmed_repository(klass, source):
        pmname = pubmed_external_ids['pubmed']['name']
        args = {
                "name" : pmname,
                "source" : source,
                "log" : "Created by %s" % source
                }
        return Repository.find_or_create_by_name(args)

class OpenMetaCommon(ModelBase):
    "Common fields shared by Rating and Instance tables."
    free_to_read = BooleanField(null=True,
            help_text="Are journal contents available online for free?")
    license = ForeignKeyField(License, null=True)
    start_date = DateField(null=True,
            help_text="This rating's properties are in effect commencing from this date.")
    end_date = DateField(null=True,
            help_text="This rating's properties are in effect up to this date.")

    def validate_downloadable(self):
        """
        Validate that the article is available at the designated URL and
        corresponds to expected or min file size and expected file type, if
        provided.
        """
        raise Exception("not implemented")

class Rating(OpenMetaCommon):
    journal = ForeignKeyField(Journal, related_name="ratings")

    def __unicode__(self):
        return u"<Rating {1} on {0}>".format(self.journal.title, self.id)

class Instance(OpenMetaCommon):
    article = ForeignKeyField(Article, related_name="instances")
    repository = ForeignKeyField(Repository,
        help_text="Repository in which this instance is deposited or described.")
    identifier = CharField(null=True,
            help_text = "Identifier within the repository.")
    info_url = CharField(null=True,
            help_text = "For convenience, URL of an info page for the article.")
    download_url = CharField(null=True,
            help_text = "URL for directly downloading the article. May be tested for status and file size.")
    expected_file_size = CharField(null = True,
            help_text = "Expected file size if article is downloadable.")
    expected_file_hash = CharField(null = True,
            help_text = "Expected file checksum if article is downloadable.")

    def __unicode__(self):
        if self.license is None:
            license_alias = "None"
        else:
            license_alias = self.license.alias

        return u"<Instance {0} (id: {2}) in {1} license? {3} ftr? {4}>".format(self.id, self.repository.name, self.identifier, license_alias, self.free_to_read)

    @classmethod
    def create_pmid(klass, article, pubmed_id, source):
        return klass.create(
                article=article,
                repository=Repository.pubmed_repository(source),
                source=source,
                log="Created by %s" % source
                )

class JournalList(ModelBase):
    name = CharField()

    def __unicode__(self):
        args = (len(self.journals()), self.name, self.id)
        return u"<Journal List {2} ({0}): {1}>".format(*args)

    def __len__(self):
        return self.memberships.count()

    def __getitem__(self, key):
        return self.memberships[key].journal

    def add_journal(self, journal, source):
        JournalListMembership(
            journal_list = self,
            source = source,
            log = source,
            journal = journal
        ).save()

    def journals(self):
        return [membership.journal for membership in self.memberships]

class JournalListMembership(ModelBase):
    journal_list = ForeignKeyField(JournalList, related_name="memberships")
    journal = ForeignKeyField(Journal, related_name="memberships")

class ArticleList(ModelBase):
    name = CharField()
    orcid = CharField(null=True)

    def __unicode__(self):
        args = (len(self.articles()), self.name)
        return u"<Article List ({0} articles): {1}>".format(*args)

    def __len__(self):
        return self.memberships.count()

    def __getitem__(self, key):
        return self.memberships[key].article

    def add_article(self, article, source):
        ArticleListMembership(
            article_list = self,
            source = source,
            log = source,
            article = article
        ).save()

    def articles(self):
        return [membership.article for membership in self.memberships]

class ArticleListMembership(ModelBase):
    article_list = ForeignKeyField(ArticleList, related_name="memberships")
    article = ForeignKeyField(Article, related_name="memberships")

model_classes = [Article, ArticleList, ArticleListMembership, Instance,
        Journal, JournalList, JournalListMembership, License, LicenseAlias,
        Publisher, Rating, Repository]

license_classes = [License, LicenseAlias]

def create_db_tables():
    for klass in model_classes:
        klass.create_table()

def delete_all(delete_licenses = False):
    for klass in model_classes:
        if delete_licenses or klass not in license_classes:
            klass.delete().execute()
