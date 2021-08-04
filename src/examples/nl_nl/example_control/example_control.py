from ....mcfg import CategoryMeta, AbsRule, AbsGrammar
# from ..span_realization import abstree_to_labeledtree, get_matchings
from ..span_realization import (abstree_to_labeledtree, labeled_tree_to_realization, get_matchings,
                                project_tree, get_choices, realize_span)
from pprint import pprint

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
from pprint import pprint

def map_tree(tree, f):
    if isinstance(tree, CategoryMeta):
        return f(tree)
    head, children = tree
    return f(head), tuple(map(lambda c: map_tree(c, f), children))

# from src.examples.nl_nl.example_control.example_control import *
def main(max_depth: int):
    trees = [tree for depth in range(max_depth) for tree in grammar.generate(goal=S, depth=depth)]
    labeled_trees = list(map(lambda t: abstree_to_labeledtree(t, n_candidates, v_candidates,
                                                              iter(range(10)), iter(range(10))), trees))
    realizations = list(map(lambda t: labeled_tree_to_realization(t, surf_rules, [], [])[1], labeled_trees))
    matchings = list(map(lambda t: get_matchings(t, matching_rules), labeled_trees))
    choices = list(map(lambda t: get_choices(project_tree(t), exclude_candidates), labeled_trees))
    realized = [[realize_span(option, span_realization[0]) for option in options]
                for span_realization, options in zip(realizations, choices)]
    return trees, realized, matchings
