#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

from bs4 import BeautifulSoup

def parse(demux_stats):
    """parses the Demultiplex_Stats.htm

    Args:
        demux_stats (str): a path to Demultiplex_Stats.htm of the run
        unaligneddir (str): name of the Unaligned dir

    Returns: TODO

    """

    samples = {} # lane: sample_id: {}

    soup = BeautifulSoup(open(demux_stats), 'html.parser')
    tables = soup.findAll("table")
    rows = tables[1].findAll('tr')
    for row in rows:
        sample = {}
        cols = row.findAll('td')

        lane = cols[0].string.encode('utf8')
        if not lane in samples:
            samples[lane] = {}

        sample_name = cols[1].string.encode('utf8')
        sample['sample_name'] = sample_name
        sample['barcode'] = cols[3].string.encode('utf8')
        sample['project_id'] = cols[6].string.encode('utf8')
        sample['lane'] = lane
        sample['yield_mb'] = int(cols[7].string.encode('utf8').replace(",",""))
        sample['pf_pc'] = float(cols[8].string.encode('utf8'))
        sample['readcounts'] = int(cols[9].string.encode('utf8').replace(",",""))
        sample['raw_clusters_pc'] = float(cols[10].string.encode('utf8'))
        sample['perfect_barcodes_pc'] = float(cols[11].string.encode('utf8'))
        sample['q30_bases_pc'] = float(cols[13].string.encode('utf8'))
        sample['mean_quality_score'] = float(cols[14].string.encode('utf8'))

        samples[lane][sample_name] = sample

    return samples
