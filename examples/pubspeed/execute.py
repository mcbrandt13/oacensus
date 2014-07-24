__author__ = 'cneylon'

import yaml
import os
import os.path
import subprocess

# All journals except PLOS ONE
JOURNALS = ["Current Biology : CB",
            "Nature Neuroscience",
            "Genes & development",
            "Bioinformatics",
            "Cell",
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
            "eLife",
            "Nature communications",
            "Scientific reports"]

DATE_PERIODS = [('2012-01-01', '2012-12-31'),
				('2013-01-01', '2013-12-31'),
				('2014-01-01', '2014-06-30')]
            
jrnl_term = "(" + " OR ".join(['("%s"[Journal])' % title for title in JOURNALS]) + ")"

#Other journals
for period in DATE_PERIODS:
	date_term = 'AND ("%s"[EDAT] : "%s"[EDAT]) AND "journal article"[Publication Type]' % period
	search_term = "'%s %s'" % (jrnl_term, date_term)
	path = 'run/all_jrnls_' + period[0]
	if not os.path.isdir(path):
		os.makedirs(path)
	
	yelems = (
				search_term,
				period[0][0:7],
				period[1][0:7]
			)
	yaml = """
- pubmed:
    search: %s
    start-period: %s
    end-period: %s 
""" % yelems

	yaml_path = os.path.join(path, 'oacensus.yaml')
	with open(yaml_path, 'w') as f:
		f.write(yaml)
		
	os.chdir(path)
	subprocess.call(['oacensus', 'run', '--config', 'oacensus.yaml', '--reports', 'pubspeed-excel'])
	os.chdir('../..')
	
for period in DATE_PERIODS:
	date_term = 'AND ("%s"[EDAT] : "%s"[EDAT]) AND "journal article"[Publication Type]' % period
	search_term = """'"PLoS one"[Journal] %s'""" % (date_term)
	path = 'run/pone_' + period[0]
	if not os.path.isdir(path):
		os.makedirs(path)
	
	yelems = (
				search_term,
				period[0][0:7],
				period[1][0:7]
			)
	yaml = """
- pubmed:
    search: %s
    start-period: %s
    end-period: %s 
""" % yelems

	yaml_path = os.path.join(path, 'oacensus.yaml')
	with open(yaml_path, 'w') as f:
		f.write(yaml)
		
	os.chdir(path)
	subprocess.call(['oacensus', 'run', '--config', 'oacensus.yaml', '--reports', 'pubspeed-excel'])
	os.chdir('../..')

	
	