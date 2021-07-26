import os
data_folder = '/Users/gijswijnholds/PycharmProjects/lexiconl/data'

noun_fn = os.path.join(data_folder, 'processed/alle_personen.txt')
all_nouns = [ln.strip() for ln in open(noun_fn, 'r').readlines()]

de_noun_fn = os.path.join(data_folder, 'processed/de_personen.txt')
het_noun_fn = os.path.join(data_folder, 'processed/het_personen.txt')
de_nouns = [ln.strip() for ln in open(de_noun_fn, 'r').readlines()]
het_nouns = [ln.strip() for ln in open(het_noun_fn, 'r').readlines()]