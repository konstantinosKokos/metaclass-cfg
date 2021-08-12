from src import cwdir
import os

data_dir = os.path.join(cwdir, 'examples/nl_nl/data/')

de_noun_fn = os.path.join(data_dir, 'de_personen.txt')
het_noun_fn = os.path.join(data_dir, 'het_personen.txt')
obj_cv_fn = os.path.join(data_dir, 'obj_control_verbs.txt')
sub_cv_fn = os.path.join(data_dir, 'sub_control_verbs.txt')
inf_fn = os.path.join(data_dir, 'infinitives.txt')

de_nouns = [ln.strip() for ln in open(de_noun_fn, 'r').readlines()]
het_nouns = [ln.strip() for ln in open(het_noun_fn, 'r').readlines()]


def load_control_verbs(fn: str) -> tuple[list[str], list[str]]:
    with open(fn, 'r') as infile:
        verbs_present, verbs_inf = zip(*[ln.strip().split('\t') for ln in infile.readlines()])
    return list(verbs_present), list(verbs_inf)


obj_control_verbs_present, obj_control_verbs_inf = load_control_verbs(obj_cv_fn)
sub_control_verbs_present, sub_control_verbs_inf = load_control_verbs(sub_cv_fn)
infinitive_verbs = [ln.strip() for ln in open(inf_fn).readlines()]

