from src.mcfg import Category, CategoryMeta, Rule, Grammar, realize_trees
from src.example_utils import get_nouns, simple_concat, simple_flatten
from src.mcfg import realize_surface, realize_span

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

TV_ctrl = CategoryMeta('TV_ctrl')
INF_ctrl = CategoryMeta('INF_ctrl')
ITV_inf = CategoryMeta('ITV_inf')
TV_inf = CategoryMeta('TV_inf')
ADJ = CategoryMeta('ADJ')

# Constants

NP_s.constants = get_nouns(4)
NP_o.constants = get_nouns(4)
NP_o2.constants = get_nouns(4)
NP_inf.constants = ['het biertje', 'een pizza']
ADJ.constants = ['depressieve']

TE.constants = ['te']
ITV_inf.constants = ['vertrekken', 'komen', 'verliezen', 'winnen']
TV_inf.constants = ['drinken', 'eten']

TV_ctrl.constants = ['belooft', 'vraagt', 'dwingt', 'garandeert']
INF_ctrl.constants = ['beloven', 'vragen', 'dwingen', 'garanderen']

INF_tv.constants = [('het biertje', 'drinken'), ('een pizza', 'eten')]


rules = Rule.from_list([
        (S, (CTRL,), simple_concat(S), simple_flatten),
        (CTRL, (NP_s, TV_ctrl, NP_o, VC), simple_concat(CTRL), simple_flatten),
        (VC, (TE, INF),  simple_concat(VC), simple_flatten),
        (INF, (ITV_inf,),  simple_concat(INF), simple_flatten),
        # (VC, (NP_inf, TE, TV_inf), simple_concat(INF), simple_flatten)
        (VC, (INF_tv, TE), lambda inf_tv, te: VC(f'{inf_tv[0]} {te[0]} {inf_tv[1]}'),
                           lambda inf_tv, te: (inf_tv[0] + te[0] + inf_tv[1],)),
        (VC, (NP_o2, TE, INF_ctrl, VC), simple_concat(VC), simple_flatten),
        # (NP_o, (ADJ, NP_o), simple_concat(NP_o), simple_flatten)
    ])


# abs_rules = [(S , (CTRL,)), ...]
#
# conc_rules = [(STRING, (STRING,)),
#               (STRING, STRING)]
#
# surface_imp = {(S , (CTRL,)): [simple_concat(S)]}
#

grammar = Grammar(rules)
trees = grammar.generate(S, 4, True)
from pprint import pprint
# real_trees = realize_trees(trees)
# pprint(real_trees)
