from ....mcfg import CategoryMeta, AbsRule, AbsGrammar
from ..span_realization import (abstree_to_labeledtree, labeled_tree_to_realization, get_matchings,
                                project_tree, get_choices, realize_span)

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
PREF.constants = ['(Iemand ziet)']
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


def main(max_depth: int):
    trees = [tree for depth in range(max_depth) for tree in grammar.generate(goal=S, depth=depth)]
    labeled_trees = list(map(lambda t: abstree_to_labeledtree(t, n_candidates, v_candidates,
                                                              iter(range(10)), iter(range(10))), trees))
    realizations = list(map(lambda t: labeled_tree_to_realization(t, surf_rules, [], [])[1], labeled_trees))
    matchings = list(map(lambda t: get_matchings(t, matching_rules), labeled_trees))
    choices = list(map(lambda t: get_choices(project_tree(t)), labeled_trees))
    realized = [[realize_span(option, span_realization[0]) for option in options]
                for span_realization, options in zip(realizations, choices)]
    return trees, realized, matchings
