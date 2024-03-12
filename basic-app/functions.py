import pandas as pd
import numpy as np

# function to parse nucleotide mutation files
def parse_mutation_files(filename):
    df = pd.read_csv(filename, sep='\t')
    df.columns = ['position', 'counts']
    mut_list = []
    for x, y in zip(df.counts.tolist(), df.position.tolist()):
        mut_list.extend([y] * x)
    return mut_list

# function to make mutation dataframe
def mutation_df():
    chronic = parse_mutation_files('/Users/egill/Projects/chronic_infection_python/basic-app/data/chronicnucl.tsv')
    deer = parse_mutation_files('/Users/egill/Projects/chronic_infection_python/basic-app/data/deernucl.tsv')
    global_mut = parse_mutation_files('/Users/egill/Projects/chronic_infection_python/basic-app/data/globalnucl.tsv')
    
    mut_dict = {'chronic': chronic,
                'deer': deer,
                'global': global_mut}
    
    df = pd.DataFrame.from_dict(mut_dict, orient='index').T.reset_index(drop=True)
    return df


# function to parse gene files
def parse_gene_files(filename):
    if filename == 'gene':
        df = pd.read_csv('/Users/egill/Projects/chronic_infection_python/basic-app/data/genes.csv')
        genelist = df['start'].tolist()
        names = df['gene'].tolist()
    elif filename == 'genes_split':
        df = pd.read_csv('/Users/egill/Projects/chronic_infection_python/basic-app/data/genes_split.csv')
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

# function to put mutations in bins
def get_counts(df):
    pass