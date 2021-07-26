from mcfg.mcfg import Category, CategoryMeta, Rule, Grammar, realize_trees
from mcfg.example_utils import get_nouns, simple_concat

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
TV_inf_ctrl = CategoryMeta('TV_inf_ctrl')

VC = CategoryMeta('VC')

# Constants
NP_s.constants = get_nouns(4)
NP_s2.constants = get_nouns(4)
NP_o.constants = ['het biertje', 'een pizza']
PREF.constants = ['(Iemand ziet)']
TE.constants = ['te']

ITV_inf_action.constants = ['dansen', 'zingen']
TV_inf_action.constants = ['drinken', 'eten']
TV_inf_sense.constants = ['zien', 'horen', 'ruiken', 'voelen', 'leren', 'helpen']
TV_inf_ctrl.constants = ['beloven', 'vragen']



# S(XYZ) -> PREF(X) EMB(Y, Z)
# PREF -> '(Iemand ziet)'
#
# EMB(X, Y) -> NP_s(X) ITV_inf_action(Y)

# (Iemand ziet) [de man] de vrouw een biertje, [zien] drinken
# EMB(XY, Z) -> NP_s(X) NP_o(Y) TV_inf_action(Z)

# (Iemand ziet) [de man] de vrouw [zien] drinken
# EMB(XY, ZW) -> NP_s(X) TV_inf_sense(Z) EMB(Y, W)

# (Iemand ziet) de man de vrouw leren dansen
# (Iemand ziet) de man de vrouw leren te dansen
# (Iemand ziet) de man de vrouw leren om te dansen
# (Iemand ziet) [de man]11 [de vrouw]12 [leren]1 een biertje te drinken
# (Iemand ziet) [de man]11 de vrouw de kinderen leren zien zwemmen

# (Iemand ziet) de man de vrouw beloven te dansen
# (Iemand ziet) de man de vrouw beloven om te dansen
# (Iemand ziet) de man de vrouw beloven om de kinderen te leren dansen
# (Iemand ziet) de man de vrouw beloven een biertje te drinken
# EMB(XY, ZW) -> NP_s(X) NP_o(Y) TV_inf_ctrl(Z) VC(W)
# VC(XY) -> TE(X) ITV_inf_action(Y)

# (Iemand weet dat) de man de vrouw de kinderen ziet leren zwemmen
# (Iemand weet dat) de man de vrouw leert de kinderen te zien zwemmen
# EMB(XY, ZW) -> NP_s() NP_o() TV_inf_instruct VC(W)

#
# EMB(de man de vrouw de kinderen, ziet beloven te dansen) ->
# EMB(de vrouw de kinderen, beloven te dansen) ->
# EMB(XY, ZWU)



rules = Rule.from_list([
        (S, (PREF, EMB), lambda pref, emb: S(f'{pref[0]} {emb[0]} {emb[1]}')),
        (EMB, (NP_s, ITV_inf_action), lambda np_s, itv_inf_action: EMB(np_s[0], itv_inf_action[0])),
        (EMB, (NP_s, NP_o, TV_inf_action), lambda np_s, np_o, tv_inf_action: EMB(f'{np_s[0]} {np_o[0]}', tv_inf_action[0])),
        (EMB, (NP_s, TV_inf_sense, EMB), lambda np_s, tv_inf_sense, emb: EMB(f'{np_s[0]} {emb[0]}', f'{tv_inf_sense[0]} {emb[1]}')),
        (EMB, (NP_s, NP_s2, TV_inf_ctrl, VC), lambda np_s, np_o, tv_inf_ctrl, vc: EMB(f'{np_s[0]} {np_o[0]}', f'{tv_inf_ctrl[0]} {vc[0]}')),
        (VC, (TE, ITV_inf_action), simple_concat(VC))
    ])


grammar = Grammar(rules)
trees = grammar.generate(S, 5, True)
from pprint import pprint
pprint(realize_trees(trees))
