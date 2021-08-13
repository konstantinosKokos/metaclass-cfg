"""
Pseudo-code for the description of the grammar.

Recursive control verb declarative sentences:
"De man belooft de vrouw te vertrekken"
"De man vraagt de vrouw te vertrekken"
"De man belooft de vrouw de kinderen te beloven te vertrekken"
"De man vraagt de vrouw de kinderen te vragen te vertrekken"

S -> CTRL
CTRL -> NP_s TV_ctrl NP_o VC
VC -> TE INF
VC -> NP TE INF_ctrl VC
INF -> ITV_inf
INF -> INF_tv(2)
INF_tv(np, 'te' vp) -> NP_inf(np) TE TV_inf(vp)

NP_inf -> 'het biertje', 'een pizza'
NP_s -> 'de man', 'de vrouw', 'het kind'
NP_o -> 'de sollicitant', 'het meisje', 'de socialist'
NP_o2 -> '', '

TV_ctrl -> 'belooft', 'vraagt', 'dwingt', 'garandeert'
INF_ctrl -> 'beloven', 'vragen', 'dwingen', 'garanderen'

TE -> 'te'
ITV_inf -> 'vertrekken', 'komen', 'verliezen', 'winnen'
TV_inf -> 'drinken', 'eten'

"""


import os.path
from ....mcfg import CategoryMeta, AbsRule, AbsGrammar, AbsTree, Tree, T
from typing import Callable, Iterator
from typing import Optional as Maybe
from ..span_realization import (abstree_to_labeledtree, labeled_tree_to_realization, get_matchings,
                                project_tree, get_choices, realize_span, Matching, Realized, sample_choices)
from ..lexicon import Lexicon
from random import seed as set_seed
from random import shuffle
import json


def map_tree(tree: Tree[CategoryMeta], f: Callable[[CategoryMeta], T]) -> Tree[T]:
    if isinstance(tree, CategoryMeta):
        return f(tree)
    head, children = tree
    return f(head), tuple(map(lambda c: map_tree(c, f), children))


# Categories
S = CategoryMeta('S')
CTRL = CategoryMeta('CTRL')

VC = CategoryMeta('VC')
INF = CategoryMeta('INF')
INF_tv = CategoryMeta('INF_tv', 2)

TE = CategoryMeta('TE')

NP_s = CategoryMeta('NP_s')
NP_o = CategoryMeta('NP_o')
NP_o2 = CategoryMeta('NP_o2')
NP_inf = CategoryMeta('NP_inf')

TV_su_ctrl = CategoryMeta('TV_su_ctrl')
TV_obj_ctrl = CategoryMeta('TV_obj_ctrl')
INF_su_ctrl = CategoryMeta('INF_su_ctrl')
INF_obj_ctrl = CategoryMeta('INF_obj_ctrl')
ITV_inf = CategoryMeta('ITV_inf')
TV_inf = CategoryMeta('TV_inf')
DIE = CategoryMeta('DIE')
REL_su_VERB = CategoryMeta('REL_su_VERB')
REL_obj_VERB = CategoryMeta('REL_obj_VERB')

# Constants
NP_s.constants = ['de man', 'de vrouw', 'het kind']
NP_o.constants = ['de sollicitant', 'het meisje', 'de socialist']
NP_o2.constants = ['de agent', 'het opaatje', 'de geitenhoeder']
NP_inf.constants = ['het biertje', 'een pizza']

TE.constants = ['te']
ITV_inf.constants = ['vertrekken', 'komen', 'verliezen', 'winnen']
TV_inf.constants = ['drinken', 'eten']

TV_su_ctrl.constants = ['belooft', 'garandeert']
TV_obj_ctrl.constants = ['vraagt', 'dwingt']
INF_su_ctrl.constants = ['beloven', 'garanderen']
INF_obj_ctrl.constants = ['vragen', 'dwingen']

INF_tv.constants = [('het biertje', 'drinken'), ('een pizza', 'eten')]
DIE.constants = ['die']

REL_su_VERB.constants = ['helpt', 'bijstaat']
REL_obj_VERB.constants = ['negeert', 'verpleegt']


annotated_rules = [
        ((S,            (CTRL,)),
         (dict(),       (False,)),
         ([(0, 0)],)),
        ((CTRL,         (NP_s, TV_su_ctrl, NP_o, VC)),
         ({1: 0},       (False, False, False, 0)),
         ([(0, 0), (1, 0), (2, 0), (3, 0)],)),
        ((CTRL,         (NP_s, TV_obj_ctrl, NP_o, VC)),
         ({1: 0},       (False, False, False, 2)),
         ([(0, 0), (1, 0), (2, 0), (3, 0)],)),
        ((VC,           (TE, INF)),
         (dict(),       (False, True)),
         ([(0, 0), (1, 0)],)),
        ((INF,          (ITV_inf,)),
         ({0: None},    (False,)),
         ([(0, 0)],)),
        ((VC,           (INF_tv, TE)),
         ({0: None},    (False, False)),
         ([(0, 0), (1, 0), (0, 1)],)),
        ((VC,           (NP_o2, TE, INF_su_ctrl, VC)),
         ({2: None},    (False, False, False, True)),
         ([(0, 0), (1, 0), (2, 0), (3, 0)],)),
        ((VC,           (NP_o2, TE, INF_obj_ctrl, VC)),
         ({2: None},    (False, False, False, 0)),
         ([(0, 0), (1, 0), (2, 0), (3, 0)],)),
        ((NP_s,         (NP_s, DIE, NP_o, REL_su_VERB)),
         ({3: 0},       (False, False, False, False)),
         ([(0, 0), (1, 0), (2, 0), (3, 0)],)),
        ((NP_s,         (NP_s, DIE, NP_o, REL_obj_VERB)),
         ({3: 2},       (False, False, False, False)),
         ([(0, 0), (1, 0), (2, 0), (3, 0)],))
]

n_candidates = {NP_s, NP_o, NP_o2}
v_candidates = {TV_su_ctrl, TV_obj_ctrl, ITV_inf, INF_su_ctrl, INF_obj_ctrl, REL_su_VERB, REL_obj_VERB, INF_tv}

grammar = AbsGrammar(AbsRule.from_list([r[0] for r in annotated_rules]))

matching_rules = {AbsRule(lhs, rhs): matching_rule for ((lhs, rhs), matching_rule, _) in annotated_rules}
surf_rules = {AbsRule(lhs, rhs): surf_rule for ((lhs, rhs), _, surf_rule) in annotated_rules}

exclude_candidates = {DIE, TE}


def get_string_trees(trees: list[AbsTree]):
    return list(map(lambda t: map_tree(t, lambda n: n.__name__), trees))


def set_constants(nouns: list[str], su_verbs: list[str], su_verbs_inf: list[str],
                  obj_verbs: list[str], obj_verbs_inf: list[str]):
    n_idx = len(nouns)//3
    NP_s.constants = nouns[:n_idx]
    NP_o.constants = nouns[n_idx:2*n_idx]
    NP_o2.constants = nouns[2*n_idx:]

    TV_su_ctrl.constants = su_verbs
    TV_obj_ctrl.constants = obj_verbs
    INF_su_ctrl.constants = su_verbs_inf
    INF_obj_ctrl.constants = obj_verbs_inf


def get_grammar(max_depth: int, sample: Maybe[int] = None) -> Iterator[str]:
    def choice_fn(c: list[CategoryMeta]):
        if sample is None:
            return get_choices(c, exclude_candidates)
        return sample_choices(c, sample, exclude_candidates)

    for depth in range(max_depth):
        for tree in grammar.generate(S, depth):
            labeled_tree = abstree_to_labeledtree(tree, n_candidates, v_candidates, iter(range(999)), iter(range(999)))
            realization = labeled_tree_to_realization(labeled_tree, surf_rules, [], [])[1]
            matching = get_matchings(labeled_tree, matching_rules)
            projection = project_tree(labeled_tree)
            surfaces = [realize_span(choice, realization[0]) for choice in choice_fn(projection)]
            # yield tree, labeled_tree, realization[0], matching, projection, surfaces
            yield matching, surfaces


def json_string(matching: Matching, surfaces: list[Realized]):
    return json.dumps({'matching': matching, 'surfaces': surfaces})


def main(max_depth: int, out_fn: str, noun_idxs: tuple[int, int], su_verb_idxs: tuple[int, int],
         obj_verb_idxs: tuple[int, int], num_samples: Maybe[int] = None, seed: Maybe[int] = None):
    all_nouns = Lexicon.de_nouns()
    su_verbs = Lexicon.sub_control_verbs_present()
    su_verbs_inf = Lexicon.sub_control_verbs_inf()
    obj_verbs = Lexicon.obj_control_verbs_present()
    obj_verbs_inf = Lexicon.obj_control_verbs_inf()

    if seed is not None:
        set_seed(seed)
        shuffle(all_nouns)
        shuffle(su_verbs)
        shuffle(su_verbs_inf)
        shuffle(obj_verbs)
        shuffle(obj_verbs_inf)

    (noun_l, noun_r) = noun_idxs
    (su_verb_l, su_verb_r) = su_verb_idxs
    (obj_verb_l, obj_verb_r) = obj_verb_idxs
    print(all_nouns[noun_l:noun_r])
    set_constants(nouns=all_nouns[noun_l:noun_r],
                  su_verbs=su_verbs[su_verb_l:su_verb_r],
                  su_verbs_inf=su_verbs_inf[su_verb_l:su_verb_r],
                  obj_verbs=obj_verbs[obj_verb_l:obj_verb_r],
                  obj_verbs_inf=obj_verbs_inf[obj_verb_l:obj_verb_r])

    if os.path.isfile(out_fn):
        os.remove(out_fn)
    with open(out_fn, 'a') as out_file:
        for i, (matching, surfaces) in enumerate(get_grammar(max_depth, num_samples)):
            out_file.write(json_string(matching, surfaces) + '\n')
