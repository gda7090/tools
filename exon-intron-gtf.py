# Source Generated with Decompyle++
# File: gtf2fa_exon_intron_parallel_general.pyc (Python 2.7)

import sys
import re
import time
import argparse
import collections
from Bio import SeqIO
from Bio.Seq import Seq
from multiprocessing import Pool, cpu_count
parser = argparse.ArgumentParser(description = 'extract exon and intron sequence from ensembl sequence fasta file and gtf file')
parser.add_argument('--fa', help = 'ensembl sequence fasta file', required = True)
parser.add_argument('--gtf', help = 'ensembl gtf file', required = True)
argv = vars(parser.parse_args())
par_fa = argv['fa']
par_gtf = argv['gtf']

def reverse_complement(seq):
    return str(Seq(seq).reverse_complement())


def get_seq(fa_file):
    fa = { }
    for seq_record in SeqIO.parse(fa_file, 'fasta'):
        fa[seq_record.id] = str(seq_record.seq)
    
    return fa


def get_transcript(gtf_file):
    transcripts = { }
    kk = 0
    for eachLine in open(gtf_file):
        if eachLine.strip() != '':
            temp = eachLine.split()
            if temp[2] == 'exon':
                transcript_id = re.search('transcript_id "(.+?)"', eachLine).group(1).strip()
                if transcript_id not in transcripts:
                    transcripts[transcript_id] = { }
                    transcripts[transcript_id]['order'] = kk
                    transcripts[transcript_id]['exon_order'] = 0
                    transcripts[transcript_id]['chr'] = temp[0].strip()
                    transcripts[transcript_id]['strand'] = temp[6].strip()
                    transcripts[transcript_id]['exon'] = collections.OrderedDict()
                    kk += 1
                if not transcripts[transcript_id]['strand'] == temp[6].strip():
                    raise AssertionError
                if not None[transcript_id]['chr'] == temp[0].strip():
                    raise AssertionError
                None[transcript_id]['exon_order'] += 1
                transcripts[transcript_id]['exon'][str(transcripts[transcript_id]['exon_order'])] = [
                    int(temp[3].strip()),
                    int(temp[4].strip())]
            
    return transcripts


def main_flow(eachscript):
    res = { }
    res['exon_res'] = []
    res['intron_res'] = []
    res['order'] = transcripts[eachscript]['order']
    DNA = []
    for eachexon in transcripts[eachscript]['exon']:
        exon_start = transcripts[eachscript]['exon'][eachexon][0]
        exon_end = transcripts[eachscript]['exon'][eachexon][1]
        res['exon_res'].append('>' + eachscript + '_exon' + eachexon + '\n')
        if transcripts[eachscript]['strand'] == '-':
            sequence = reverse_complement(fa[transcripts[eachscript]['chr']][exon_start - 1:exon_end])
        else:
            sequence = fa[transcripts[eachscript]['chr']][exon_start - 1:exon_end]
        res['exon_res'].append(sequence + '\n')
        for i in range(exon_start, exon_end + 1):
            DNA.append(i)
        
    
    min_base = min(DNA)
    max_base = max(DNA)
    k = 0
    flag = 0
    intron = { }
    for eachbase in range(min_base, max_base + 1):
        if eachbase in DNA or flag == 0:
            k += 1
            intron[k] = []
            flag = 1
        
        flag = 0
        intron[k].append(eachbase)
    
    for eachintron in intron:
        if intron[eachintron] != []:
            intron_start = intron[eachintron][0]
            intron_end = intron[eachintron][-1]
            if not int(intron_start) <= int(intron_end):
                raise AssertionError
            None['intron_res'].append('>' + eachscript + '_intron' + str(eachintron) + '\n')
            if transcripts[eachscript]['strand'] == '-':
                sequence = reverse_complement(fa[transcripts[eachscript]['chr']][intron_start - 1:intron_end])
            else:
                sequence = fa[transcripts[eachscript]['chr']][intron_start - 1:intron_end]
        res['intron_res'].append(sequence + '\n')
        continue
    
    return res

if __name__ == '__main__':
    print time.ctime()
    fa = get_seq(par_fa)
    transcripts = get_transcript(par_gtf)
    parallel_result = []
    pool = Pool(processes = cpu_count() / 2)
    for eachscript in transcripts:
        parallel_result.append(pool.apply_async(main_flow, (eachscript,)))
    
    pool.close()
    pool.join()
    continue
    result = [ '' for i in range(len(transcripts)) ]
    for eachone in parallel_result:
        temp = eachone.get()
        result[temp['order']] = temp
    
    exon_result = []
    intron_result = []
    for eachone in result:
        exon_result += eachone['exon_res']
        intron_result += eachone['intron_res']
    
    open('exon.fa', 'w').writelines(exon_result)
    open('intron.fa', 'w').writelines(intron_result)
    print time.ctime()
