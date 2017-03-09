#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

from bs4 import BeautifulSoup

def parse(demux_stats):
    """parses the Demultiplex_Stats.htm

    Args:
        demuxdir (str): a path to demux dir of the run
        unaligneddir (str): name of the Unaligned dir

    Returns: TODO

    """

    samples = {} # sample_id: {}

    soup = BeautifulSoup(open(demux_stats), 'html.parser')
    tables = soup.findAll("table")
    rows = tables[1].findAll('tr')
    for row in rows:
        sample = {}
        cols = row.findAll('td')
        sample_name = unicode(cols[1].string).encode('utf8')
        sample['sample_name'] = sample_name
        sample['barcode'] = unicode(cols[3].string).encode('utf8')
        sample['project_id'] = unicode(cols[6].string).encode('utf8')
        sample['lane'] = unicode(cols[0].string).encode('utf8')
        sample['yield_mb'] = unicode(cols[7].string).encode('utf8').replace(",","")
        sample['pf_pc'] = unicode(cols[8].string).encode('utf8')
        sample['readcounts'] = unicode(cols[9].string).encode('utf8').replace(",","")
        sample['raw_clusters_pc'] = unicode(cols[10].string).encode('utf8')
        sample['perfect_barcodes_pc'] = unicode(cols[11].string).encode('utf8')
        sample['q30_bases_pc'] = unicode(cols[13].string).encode('utf8')
        sample['mean_quality_score'] = unicode(cols[14].string).encode('utf8')

        samples[sample_name] = sample

    return samples
