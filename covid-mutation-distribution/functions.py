import pandas as pd
import numpy as np
import re
import math

example_mutation_list = [897, 3431, 7842, 8293, 8393, 11042, 12789, 13339, 15756, 18492, 21608, 21711, 21941, 22032, 22208, 22034, 22295, 22353, 22556, 22770, 22895, 22896, 22898, 22910, 22916, 23009, 23012, 23013, 23018, 23019, 23271, 23423, 23604, 24378, 24990, 25207, 26529, 26610, 26681, 26833, 28958]

# function to parse nucleotide mutation files
def parse_mutation_files(filename):
    df = pd.read_csv(filename, sep='\t')
    df.columns = ['position', 'counts']
    mut_list = []
    for x, y in zip(df.counts.tolist(), df.position.tolist()):
        mut_list.extend([y] * x)
    total_mutations = sum(df.counts.tolist())
    return mut_list, total_mutations

# function to parse gene files
# gene bins from Wuhan reference sequence NC_045512.2
def parse_gene_files(filename):
    if filename == 'gene':
        df = pd.read_csv('covid-mutation-distribution/genes.csv')
        genelist = df['start'].tolist()
        names = df['gene'].tolist()
    elif filename == 'genes_split':
        df = pd.read_csv('covid-mutation-distribution/genes_split.csv')
        genelist = df['start'].tolist()
        names = df['gene'].tolist()
    return genelist, names

# function to make bins
def make_bins(x, binsize):
    try:
        int(binsize)
        counts, bins0 = np.histogram(x, bins=range(1,30001,int(binsize)))
        bins0 = 0.5 * (bins0[:-1] + bins0[1:])
    except ValueError:
        if binsize == 'gene':
            genebins, names = parse_gene_files('gene')
            counts, bins = np.histogram(x, bins=genebins)
            names.pop()
            bins0 = names
        else:
            genebins, names = parse_gene_files('genes_split')
            counts, bins = np.histogram(x, bins=genebins)
            names.pop()
            bins0 = names
    return counts, bins0

# function to calculate likelihood
def get_likelihood(existing_bin_counts, test_bin_counts):
    existing_bin_counts = np.array(existing_bin_counts)
    test_bin_counts = np.array(test_bin_counts)
    return np.sum(np.log(((existing_bin_counts + 1)/np.sum(existing_bin_counts + 1)) ** test_bin_counts))

# function to determine most likely distribution
def most_likely(binsize, global_, chronic, deer, mutated_nucleotide_list):
    
    try:
        mutated_nucleotide_list = mutated_nucleotide_list.split(',') 
        int_nuc_list = [re.sub('\D', '', i) for i in mutated_nucleotide_list]
        mut_nuc_list = [int(i) for i in int_nuc_list]
    except:
        return None
    mut_counts, mut_bins = make_bins(mut_nuc_list, binsize)
    # get bins for global, chronic and deer
    global_counts, global_bins = make_bins(global_,binsize)
    chronic_counts, chronic_bins = make_bins(chronic,binsize)
    deer_counts, deer_bins = make_bins(deer,binsize)
    
    # calculate all likelihoods
    global_likelihood = get_likelihood(global_counts, mut_counts)
    chronic_likelihood = get_likelihood(chronic_counts, mut_counts)
    deer_likelihood = get_likelihood(deer_counts, mut_counts)
    
    # make a list of all likelihoods, find most likely
    likelihood_list = [global_likelihood, chronic_likelihood, deer_likelihood]
    names = ['global', 'chronic', 'deer']
    zipped = list(zip(likelihood_list, names))
    best_fit = max(zipped)
    return zipped, best_fit

# function to figure out how many times more likely the fit distribution is than the default (global)
def times_more_likely(zipped_likelihood_list):
    unzipped = [i for (i, j) in zipped_likelihood_list]
    unzipped_nums = [float(i) for i in unzipped]
    return math.exp(max(unzipped_nums) - unzipped_nums[0])

# function to select palettes
def select_palette(palette_name):
    if palette_name == "viridis":
        colour_list = ['#5ec962', '#21918c', '#3b528b', '#440154']
    elif palette_name == "inferno":
        colour_list = ['#f98e09', '#bc3754', '#57106e', '#000004']
    elif palette_name == "plasma":
        colour_list = ['#f89540', '#cc4778', '#7e03a8', '#0d0887']
    return colour_list