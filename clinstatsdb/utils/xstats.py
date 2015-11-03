#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

import xml.etree.ElementTree as et
import sys
import glob
import re
import os

def xpathsum(tree, xpath):
    """Sums all numbers found at these xpath nodes

    Args:
        tree (an elementTree): parsed XML as an elementTree
        xpath (str): an xpath the XML nodes

    Returns (int): the sum of all nodes

    """
    numbers = tree.findall(xpath)
    return sum([ int(number.text) for number in numbers ])

def get_barcode_summary(tree, project, sample, barcode):
    """Calculates following statistics from the DemultiplexingStats file
    * BarcodeCount
    * PerfectBarcodeCount
    * OneMismatchBarcodeCount

    Args:
        tree (an elementTree): parsed XML as an elementTree

    Returns: TODO

    """
    barcodes = xpathsum(tree, ".//Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']//BarcodeCount".format(project=project, sample=sample, barcode=barcode))
    perfect_barcodes = xpathsum(tree, ".//Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']//PerfectBarcodeCount".format(project=project, sample=sample, barcode=barcode))
    one_mismatch_barcodes = xpathsum(tree, ".//Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']//OneMismatchBarcodeCount".format(project=project, sample=sample, barcode=barcode))

    return {
        'barcodes': barcodes,
        'perfect_barcodes': perfect_barcodes,
        'one_mismatch_barcodes': one_mismatch_barcodes,
    }

def get_summary( tree):
    """Calculates following statistics from the provided elementTree:
    * pf clusters
    * pf yield
    * pf Q30
    * raw Q30
    * pf Q Score

    Args:
        tree (an elementTree): parsed XML as an elementTree

    Returns (dict): with following keys: pf_clusters, pf_yield, pf_q30, pf_read1_yield, pf_read2_yield, pf_read1_q30, pf_read2_q30, pf_qscore_sum, pf_qscore

    """
    raw_clusters = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/ClusterCount")
    pf_clusters = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/ClusterCount")

    pf_yield = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/Yield")
    pf_read1_yield = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read[@number='1']/Yield")
    pf_read2_yield = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read[@number='2']/Yield")
    raw_yield = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/Read/Yield")
    pf_clusters_pc = pf_yield / raw_yield

    pf_q30 = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/YieldQ30")
    #raw_q30 = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/Read/YieldQ30")
    pf_read1_q30 = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read[@number='1']/YieldQ30")
    pf_read2_q30 = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read[@number='2']/YieldQ30")
    #pf_q30_bases_pc = pf_q30 / pf_yield

    pf_qscore_sum = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/QualityScoreSum")
    pf_qscore = pf_qscore_sum / pf_yield

    return {
        #'pf_q30_bases_pc': pf_q30_bases_pc,
        #'raw_q30': raw_q30,
        #'pf_clusters_pc': pf_clusters_pc,
        'raw_clusters': raw_clusters,
        'raw_yield': raw_yield,
        'pf_clusters': pf_clusters,
        'pf_yield': pf_yield,
        'pf_read1_yield': pf_read1_yield,
        'pf_read2_yield': pf_read2_yield,
        'pf_q30': pf_q30,
        'pf_read1_q30': pf_read1_q30,
        'pf_read2_q30': pf_read2_q30,
        'pf_qscore_sum': pf_qscore_sum,
        'pf_qscore': pf_qscore
    }

def get_samplesheet( demux_dir, file_name='SampleSheet.csv', delim=','):
    """Reads in and parses a samplesheet. The samplesheet is found in the provided demux_dir.
    Lines starting with #, [ and blank will be skipped.
    First line will be taken as the header.

    Args:
        demux_dir (path): FQ path of demux_dir
        delim (str): the samplesheet delimiter

    Returns (list of dicts):
        Keys are the header, values the lines.

    """
    with open(demux_dir + '/' + file_name) as sample_sheet:
        lines = [ line for line in sample_sheet.readlines() if not line.startswith(('#', '[')) and len(line) ] # skip comments and special headers
        lines = [ line.strip().split(delim) for line in lines ] # read lines

        header = lines[0]

        return [ dict(zip(header, line)) for line in lines[1:] ]

def calc_undetermined( demux_dir):
    sizes = {}
    all_files = glob.glob(demux_dir + '/l*/Project*/Sample*/*fastq.gz')
    for f in all_files:
        sample_name = re.search(r'Sample_(.*)/', f).group(1)
        if sample_name not in sizes:
            sizes[ sample_name ] = { 'size_of': 0, 'u_size_of': 0 }
        sizes[ sample_name ]['size_of'] += os.path.getsize(f)

    und_files = glob.glob(demux_dir + '/l*/Project*/Sample*/Undet*fastq.gz')
    for f in und_files:
        sample_name = re.search(r'Sample_(.*)/', f).group(1)
        sizes[ sample_name ]['u_size_of'] += os.path.getsize(f)

    proc_undetermined = {}
    for sample_name, size in sizes.items():
        proc_undetermined[ sample_name ] = float(size['u_size_of']) / size['size_of'] * 100

    return proc_undetermined

def get_lanes( sample_sheet):
    """Get the lanes from the SampleSheet

    Args:
        sample_sheet (list of dicts): a samplesheet with each line a dict. The keys are the header, the values the split line

    Returns:
        a list of lane numbers

    """
    return { line['Lane']: line  for line in sample_sheet }

def get_samples( sample_sheet):
    """TODO: Docstring for get_samples.

    Args:
        sample_sheet (list of dicts): a samplesheet with each line a dict. The keys are the header, the values the split line

    Returns (dict): lane is key, raw sample name is value

    """
    return { line['Lane']: line['SampleID'] for line in sample_sheet }

def parse( demux_dir):
    """Takes a DEMUX dir and calculates statistics for the run.

    Args:
        demux_dir [0] (str): the DEMUX dir

    """

    sample_sheet = get_samplesheet(demux_dir)
    lanes = get_lanes(sample_sheet)

    # get all % undetermined indexes / sample
    proc_undetermined = calc_undetermined(demux_dir)

    # create a { 1: [], 2: [], ... } structure
    summaries = dict(zip(lanes, [ [] for t in xrange(len(lanes))])) # init ;)

    # get all the stats numbers
    for lane, line in lanes.iteritems():
        stats_files = glob.glob('%s/l%st??/Stats/ConversionStats.xml' % (demux_dir, lane))
        index_files = glob.glob('%s/l%st??/Stats/DemultiplexingStats.xml' % (demux_dir, lane))

        if len(stats_files) == 0:
            exit("No stats file found for lane {}".format(lane))

        if len(index_files) == 0:
            exit("No index stats file found for lane {}".format(lane))

        for f in stats_files:
            tree = et.parse(f)
            summaries[ lane ].append(get_summary(tree))

        for f in index_files:
            tree = et.parse(f)
            summaries[ lane ].append(get_barcode_summary(tree, line['Project'], line['SampleName'], line['index']))

    # sum the numbers over a lane
    # create a { 1: {'raw_clusters': 0, ... } } structure
    total_lane_summary = {}
    for line in sample_sheet:
        total_lane_summary[ line['Lane'] ] = {
            #'pf_q30_bases_pc': 0,
            #'pf_clusters_pc': 0,
            'raw_clusters': 0,
            'raw_yield': 0,
            'pf_clusters': 0,
            'pf_yield': 0,
            'pf_read1_yield': 0,
            'pf_read2_yield': 0,
            'pf_q30': 0,
            'pf_read1_q30': 0,
            'pf_read2_q30': 0,
            'pf_qscore_sum': 0,
            'pf_qscore': 0,
            'flowcell': line['FCID'],
            'samplename': line['SampleID'],
            'barcodes': 0,
            'perfect_barcodes': 0,
            'one_mismatch_barcodes': 0,
        }

    for lane, summary in summaries.items():
       for summary_quart in summary:
            for key, stat in summary_quart.items():
                total_lane_summary[lane][ key ] += stat

    rs = {} # generate a dict: raw sample name is key, value is a dict of stats
    for lane, summary in total_lane_summary.items():
        rs[ summary['samplename'] ] = {
            'sample_name':     summary['samplename'],
            'flowcell':        summary['flowcell'],
            'lane':            lane,
            'raw_clusters_pc': 100, # we still only have one sample/lane ;)
            'pf_clusters':     summary['pf_clusters'],
            'pf_yield_pc':     round(summary['pf_yield'] / summary['raw_yield'] * 100, 2),
            'pf_yield':        summary['pf_yield'],
            'pf_Q30':          round(summary['pf_q30'] / summary['pf_yield'] * 100, 2),
            'pf_read1_q30':    round(summary['pf_read1_q30'] / summary['pf_read1_yield'] * 100, 2),
            'pf_read2_q30':    round(summary['pf_read2_q30'] / summary['pf_read2_yield'] * 100, 2),
            'pf_qscore':       round(summary['pf_qscore_sum'] / summary['pf_yield'], 2),
            'undetermined_pc': (summary['pf_clusters'] - summary['barcodes']) / summary['pf_clusters'] * 100,
            'undetermined_proc': round(proc_undetermined[ summary['samplename'] ], 2) if summary['samplename'] in proc_undetermined else 0,
            'barcodes':         summary['barcodes'],
            'perfect_barcodes': summary['perfect_barcodes'],
            'one_mismatch_barcodes': summary['one_mismatch_barcodes'],
        }

    return rs

def main(argv):
    from pprint import pprint
    pprint(parse(argv[0]))

if __name__ == '__main__':
    main(sys.argv[1:])


__ALL__ = [ 'parse' ]