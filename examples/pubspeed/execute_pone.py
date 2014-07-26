__author__ = 'cneylon'

import os
import os.path
import subprocess

DATE_PERIODS = [('2012-01-02', '2012-06-30'),
				('2012-07-01', '2012-12-31'),
				('2013-01-02', '2013-06-30'),
				('2013-07-01', '2013-12-31'),
				('2014-01-02', '2014-06-30')]
            
for period in DATE_PERIODS:
	date_term = 'AND "journal article"[Publication Type]' 
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

	
	