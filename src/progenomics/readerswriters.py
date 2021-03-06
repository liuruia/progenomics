import glob
import gzip
import os
import re
import pandas as pd

from Bio import SeqIO

from utils import *

def read_mmseqs_table(fin):
    names = ["query", "target", "pident", "alnlen", "mismatch", "gapopen", 
        "qstart", "qend", "tstart", "tend", "evalue", "bits"]
    table = pd.read_csv(fin, sep = "\t", names = names)
    return(table)

def read_fasta(fin):
    with open_smart(fin) as hin:
        seqs = list(SeqIO.parse(hin, "fasta"))
    return(seqs)
    
def write_fasta(seqs, fout):
    open(fout, "w").close()
    with open(fout, "a") as hout:
        for seq in seqs:
            SeqIO.write(seq, hout, "fasta")

def read_domtbl(fin_domtbl):
    domtbl = pd.read_csv(fin_domtbl, delim_whitespace = True, comment = '#',
        usecols = [0, 3, 13, 15, 16],
        names = ['gene', 'profile', 'score', 'hmm_from', 'hmm_to'],
        dtype = {'gene': str, 'profile': str, 'score': float, 'hmm_from': int,
            'hmm_to': int},
        engine = 'c'
    )
    return(domtbl)

def read_genes(fin):
    genes = pd.read_csv(fin, sep = "\t",
        names = ["gene", "genome", "orthogroup"])
    return(genes)

def read_orthogroups(fin):
    orthogroups = pd.read_csv(fin, sep = "\t", names = ["orthogroup", "cutoff"])
    return(orthogroups)

def read_species(fin):
    genomes = pd.read_csv(fin, sep = "\t", names = ["genome", "species"])
    return(genomes)

def read_orthogroups_orthofinder(fin_orthogroups):
    with open(fin_orthogroups, 'r') as hin_orthogroups:
        pangenome = {"gene": [], "genome": [], "orthogroup": []}
        header = hin_orthogroups.readline().strip()
        genomes = header.split("\t")[1:]
        for line in hin_orthogroups.readlines():
            line = line.strip().split("\t")
            orthogroup = line[0]
            for genome_ix, copies in enumerate(line[1:]):
                if copies != "":
                    for copy in copies.split(", "):
                        pangenome["gene"].append(copy)
                        pangenome["genome"].append(genomes[genome_ix])
                        pangenome["orthogroup"].append(orthogroup)
    pangenome = pd.DataFrame.from_dict(pangenome)
    return(pangenome)

def read_pangenome_orthofinder(din_orthofinder):
    din_pangenome = os.path.join(din_orthofinder,
        "OrthoFinder/Results_*/Orthogroups")
    din_pangenome = glob.glob(din_pangenome)[0]
    fin_genes_1 = os.path.join(din_pangenome, "Orthogroups.tsv")
    genes_assigned = read_orthogroups_orthofinder(fin_genes_1)
    fin_genes_2 = os.path.join(din_pangenome,
        "Orthogroups_UnassignedGenes.tsv")
    genes_unassigned = read_orthogroups_orthofinder(fin_genes_2)
    pangenome = genes_assigned.append(genes_unassigned)
    return(pangenome)

def extract_genes(fins_genomes):

    genes = pd.DataFrame()

    for fin_genome in fins_genomes:
        genome = filename_from_path(fin_genome)
        with open_smart(fin_genome) as hin:
            fasta = hin.read()
        genes_genome = re.compile(">([^ ]+)").findall(fasta)
        genes_genome = pd.DataFrame({"gene": genes_genome})
        genes_genome.loc[:, "genome"] = genome
        genes = genes.append(genes_genome)

    return(genes)
