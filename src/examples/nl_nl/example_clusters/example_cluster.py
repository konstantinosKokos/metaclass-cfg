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


"""
Pseudo-code for the description of the grammar.

Recursive control verb clusters in embedded clauses:
"(Iemand weet dat) de man de vrouw ziet dansen"
"(Iemand vraagt of) de man de vrouw de kinderen ziet horen dansen"
"(Iemand ziet) de man de vrouw leren dansen""
"(Iemand ziet) de man de vrouw de kinderen een biertje zien leren drinken"

"(Iemand ziet) de man een biertje drinken"
"(Iemand ziet) de man de vrouw een biertje zien drinken"
"(Iemand ziet) de man de vrouw zien dansen"
"(Iemand ziet) de man de vrouw de kinderen zien horen dansen"

"(Iemand ziet) de man de vrouw beloven te dansen" ?
"(Iemand ziet) de man de vrouw beloven een biertje te drinken" ?

"(Iemand ziet) de man de vrouw de kinderen beloven te leren dansen"  ?
"(Iemand ziet) de man de vrouw beloven de kinderen te leren dansen"  ?

"(Iemand ziet) de man de vrouw beloven een biertje te drinken" ?
"(Iemand ziet) de man de vrouw beloven de kinderen een biertje te laten drinken" ?

Indirect object can be left out without changing the understood subject within the cluster
Example: Omdat hij mij de kraanvogels hielp (te) vergiftigen
Example: Omdat hij de kraanvogels hielp (te) vergiftigen

de man dansen

S(XYZ) -> PREF(X) EMB(Y, Z)
PREF -> 'Iemand ziet'

EMB(X, Y) -> NP_s(X) ITV_inf_action(Y)
EMB(XY, Z) -> NP_s(X) NP_o(Y) TV_inf_action(Z)
EMB(XY, ZW) -> NP_s(X) TV_inf_sense(Z) EMB(Y, W)



# CTRL -> NP_s TV_ctrl NP_o VC
# VC -> TE INF
# VC -> NP TE INF_ctrl VC
# INF -> ITV_inf
# INF -> INF_tv(2)
# INF_tv(np, 'te' vp) -> NP_inf(np) TE TV_inf(vp)
# 
NP_s -> 'de man', 'de vrouw', 'het kind'
NP_o -> 'een biertje', 'een pizza'
# 
# TV_ctrl -> 'belooft', 'vraagt', 'dwingt', 'garandeert'
# INF_ctrl -> 'beloven', 'vragen', 'dwingen', 'garanderen'
# 
# TE -> 'te'
ITV_inf_action -> 'dansen', 'zingen'
TV_inf_action -> 'drinken', 'eten'
TV_inf_sense -> 'zien', 'horen', 'ruiken', 'voelen' 
TV_inf_instruct -> 'leren', 'helpen'

"""

# Categories
S = CategoryMeta('S')
PREF = CategoryMeta('PREF')
EMB = CategoryMeta('EMB', 2)
TE = CategoryMeta('TE')

NP_s = CategoryMeta('NP_s')
NP_s2 = CategoryMeta('NP_s2')
NP_o = CategoryMeta('NP_o')

ITV_inf_action = CategoryMeta('ITV_inf_action')
TV_inf_action = CategoryMeta('TV_inf_action')
TV_inf_sense = CategoryMeta('TV_inf_sense')
TV_su_inf_ctrl = CategoryMeta('TV_su_inf_ctrl')
TV_obj_inf_ctrl = CategoryMeta('TV_obj_inf_ctrl')

VC = CategoryMeta('VC')

# Constants
NP_s.constants = ['de man', 'de vrouw', 'het kind']
NP_s2.constants = ['de sollicitant', 'het meisje', 'de socialist']
NP_o.constants = ['het biertje', 'een pizza']
PREF.constants = ['Iemand ziet']
TE.constants = ['te']

ITV_inf_action.constants = ['dansen', 'zingen']
TV_inf_action.constants = ['drinken', 'eten']
TV_inf_sense.constants = ['zien', 'horen', 'ruiken', 'voelen', 'leren', 'helpen']
TV_su_inf_ctrl.constants = ['beloven', 'garanderen']
TV_obj_inf_ctrl.constants = ['vragen', 'dwingen']

"""
S(XYZ) -> PREF(X) EMB(Y, Z)
PREF -> '(Iemand ziet)'

EMB(X, Y) -> NP_s(X) ITV_inf_action(Y)

(Iemand ziet) [de man] de vrouw een biertje, [zien] drinken
EMB(XY, Z) -> NP_s(X) NP_o(Y) TV_inf_action(Z)

(Iemand ziet) [de man] de vrouw [zien] drinken
EMB(XY, ZW) -> NP_s(X) TV_inf_sense(Z) EMB(Y, W)

(Iemand ziet) de man de vrouw leren dansen
(Iemand ziet) de man de vrouw leren te dansen
(Iemand ziet) de man de vrouw leren om te dansen
(Iemand ziet) [de man]11 [de vrouw]12 [leren]1 een biertje te drinken
(Iemand ziet) [de man]11 de vrouw de kinderen leren zien zwemmen

(Iemand ziet) de man de vrouw beloven te dansen
(Iemand ziet) de man de vrouw beloven om te dansen
(Iemand ziet) de man de vrouw beloven om de kinderen te leren dansen
(Iemand ziet) de man de vrouw beloven een biertje te drinken
EMB(XY, ZW) -> NP_s(X) NP_o(Y) TV_inf_ctrl(Z) VC(W)
VC(XY) -> TE(X) ITV_inf_action(Y)

(Iemand weet dat) de man de vrouw de kinderen ziet leren zwemmen
(Iemand weet dat) de man de vrouw leert de kinderen te zien zwemmen
EMB(XY, ZW) -> NP_s() NP_o() TV_inf_instruct VC(W)


EMB(de man de vrouw de kinderen, ziet beloven te dansen) ->
EMB(de vrouw de kinderen, beloven te dansen) ->
EMB(XY, ZWU)

Indirect object can be left out without changing the understood subject within the cluster
Example: Omdat hij mij de kraanvogels hielp (te) vergiftigen
Example: Omdat hij de kraanvogels hielp (te) vergiftigen
"""

annotated_rules = [
        ((S,            (PREF, EMB)),
         (dict(),       (False, False)),
         ([(0, 0), (1, 0), (1, 1)],)),
        ((EMB,          (NP_s, ITV_inf_action)),
         ({1: 0},       (False, False)),
         ([(0, 0)], [(1, 0)])),
        ((EMB,          (NP_s, NP_o, TV_inf_action)),
         ({2: 0},       (False, False, False)),
         ([(0, 0), (1, 0)], [(2, 0)])),
        ((EMB,          (NP_s, TV_inf_sense, EMB)),
         ({1: 0},       (False, False, False)),
         ([(0, 0), (2, 0)], [(1, 0), (2, 1)])),
        ((EMB,          (NP_s, NP_s2, TV_su_inf_ctrl, VC)),
         ({2: 0},       (False, False, False, 0)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0)])),
        ((EMB,          (NP_s, NP_s2, TV_obj_inf_ctrl, VC)),
         ({2: 0},       (False, False, False, 1)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0)])),
        ((VC,           (TE, ITV_inf_action)),
         ({1: None},    (False, False)),
         ([(0, 0), (1, 0)],))
]

n_candidates = {NP_s, NP_o, NP_s2}
v_candidates = {ITV_inf_action, TV_inf_action, TV_inf_sense, TV_su_inf_ctrl, TV_obj_inf_ctrl}

grammar = AbsGrammar(AbsRule.from_list([r[0] for r in annotated_rules]))

matching_rules = {AbsRule(lhs, rhs): matching_rule for ((lhs, rhs), matching_rule, _) in annotated_rules}
surf_rules = {AbsRule(lhs, rhs): surf_rule for ((lhs, rhs), _, surf_rule) in annotated_rules}

def map_tree(tree: Tree[CategoryMeta], f: Callable[[CategoryMeta], T]) -> Tree[T]:
    if isinstance(tree, CategoryMeta):
        return f(tree)
    head, children = tree
    return f(head), tuple(map(lambda c: map_tree(c, f), children))


exclude_candidates = {TE}


def get_string_trees(trees: list[AbsTree]):
    return list(map(lambda t: map_tree(t, lambda n: n.__name__), trees))


def set_constants(nouns: list[str], su_verbs_inf: list[str], obj_verbs_inf: list[str]):
    n_idx = len(nouns)//3
    NP_s.constants = nouns[:n_idx]
    NP_s2.constants = nouns[n_idx:2*n_idx]
    NP_o.constants = nouns[2*n_idx:]

    TV_su_inf_ctrl.constants = su_verbs_inf
    TV_obj_inf_ctrl.constants = obj_verbs_inf


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
    all_nouns = Lexicon.de_nouns
    su_verbs_inf = Lexicon.sub_control_verbs_inf
    obj_verbs_inf = Lexicon.obj_control_verbs_inf
    if seed is not None:
        shuffle(all_nouns, set_seed(seed))
        shuffle(su_verbs_inf, set_seed(seed))
        shuffle(obj_verbs_inf, set_seed(seed))
    (noun_l, noun_r) = noun_idxs
    (su_verb_l, su_verb_r) = su_verb_idxs
    (obj_verb_l, obj_verb_r) = obj_verb_idxs
    set_constants(nouns=all_nouns[noun_l:noun_r],
                  su_verbs_inf=su_verbs_inf[su_verb_l:su_verb_r],
                  obj_verbs_inf=obj_verbs_inf[obj_verb_l:obj_verb_r])
    if os.path.isfile(out_fn):
        os.remove(out_fn)
    if seed is not None:
        set_seed(seed)
    with open(out_fn, 'a') as out_file:
        for i, (matching, surfaces) in enumerate(get_grammar(max_depth, num_samples)):
            out_file.write(json_string(matching, surfaces) + '\n')