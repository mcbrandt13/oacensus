#!/usr/bin/env python

import argparse
import re
import sys
import os
import subprocess

parser = argparse.ArgumentParser(description='Create spreadsheet report using oacensus.')
parser.add_argument('-s', '--start', action="store", required=True, help="start date for report, in format 2014-01")
parser.add_argument('-e', '--end', action="store", required=True, help="end date for report, in format 2014-06")
args = parser.parse_args()

date_regex = "[0-9]{4}\-[0-9]{2}"

if not re.search(date_regex, args.start) or not re.search(date_regex, args.end):
	print "Start/End date is invalid. Please re-enter with format YYYY-MM (and use the '-')\n"
	sys.exit

date_term = """'"journal article"[Publication Type]'"""
path = 'reports/' + args.start
if not os.path.isdir(path):
	os.makedirs(path)

yelems = (
			date_term,
			args.start,
			args.end
		)
yaml = """
- pubmed:
    search: %s
    journals : 
        - "Current Biology : CB"
        - "Nature Neuroscience" 
        - "Genes & development"
        - "Bioinformatics"
        - "Cell"
        - "Cell host & microbe"
        - "Nature genetics"
        - "Molecular systems biology"
        - "Nature"
        - "PLoS neglected tropical diseases"
        - "PLoS medicine"
        - "PLoS biology"
        - "PLoS computational biology"
        - "PLoS pathogens"
        - "The Journal of infectious diseases"
        - "Nature medicine"
        - "Genome research"
        - "BMC infectious diseases"
        - "PLoS genetics"
        - "BMC public health"
        - "Nature cell biology"
        - "The American journal of tropical medicine and hygiene"
        - "PeerJ"
        - "SpringerPlus"
        - "eLife"
        - "Nature communications"
        - "Scientific reports"
        - "PLoS one"
        - "BMJ open"
        - "British medical journal"
        - "Journal of virology"
        - "Proceedings of the national academy of sciences of the united states of america"
        - "Science (New York, N.Y.)"
    start-period : %s
    end-period : %s
    ret-max : 1000
""" % yelems

yaml_path = os.path.join(path, 'oacensus.yaml')
with open(yaml_path, 'w') as f:
	f.write(yaml)
	
os.chdir(path)
subprocess.call(['oacensus', 'run', '--config', 'oacensus.yaml', '--reports', 'pubspeed-excel'])
os.chdir('../..')

