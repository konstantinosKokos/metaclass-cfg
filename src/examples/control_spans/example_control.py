from ...mcfg import CategoryMeta, AbsRule, AbsGrammar
from .span_realization import get_top

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
INF_ctrl = CategoryMeta('INF_ctrl')
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
INF_ctrl.constants = ['beloven', 'vragen', 'dwingen', 'garanderen']

INF_tv.constants = [('het biertje', 'drinken'), ('een pizza', 'eten')]
DIE.constants = ['die']

REL_su_VERB.constants = ['eet']
REL_obj_VERB.constants = ['eet']

# rules = AbsRule.from_list([
#         (S, (CTRL,), simple_concat(S), simple_flatten),
#         (CTRL, (NP_s, TV_ctrl, NP_o, VC), simple_concat(CTRL), simple_flatten),
#         (VC, (TE, INF),  simple_concat(VC), simple_flatten),
#         (INF, (ITV_inf,),  simple_concat(INF), simple_flatten),
#         # (VC, (NP_inf, TE, TV_inf), simple_concat(INF), simple_flatten)
#         (VC, (INF_tv, TE), lambda inf_tv, te: VC(f'{inf_tv[0]} {te[0]} {inf_tv[1]}'),
#                            lambda inf_tv, te: (inf_tv[0] + te[0] + inf_tv[1],)),
#         (VC, (NP_o2, TE, INF_ctrl, VC), simple_concat(VC), simple_flatten),
#         # (NP_o, (ADJ, NP_o), simple_concat(NP_o), simple_flatten)
#     ])

default_annotation = lambda *args: tuple(args[-2:])

annotated_rules = [
        ((S,         (CTRL,)), default_annotation),
        ((CTRL,      (NP_s, TV_su_ctrl, NP_o, VC)), lambda np_s, tv, np_o, vc, su_idx, obj_idx: (get_top(np_s)[0], obj_idx)),
        ((CTRL,      (NP_s, TV_obj_ctrl, NP_o, VC)),  lambda np_s, tv, np_o, vc, su_idx, obj_idx: (su_idx, get_top(np_o)[0])),
        ((VC,        (TE, INF)), default_annotation),
        ((INF,       (ITV_inf,)), default_annotation),
        ((VC,        (INF_tv, TE)), default_annotation),
        ((VC,        (NP_o2, TE, INF_ctrl, VC)), default_annotation),
        ((NP_s,      (NP_s, DIE, NP_o, REL_su_VERB)), lambda np_s, die, np_o, verb, su_idx, obj_idx: (get_top(np_s)[0], obj_idx)),
        ((NP_s,      (NP_s, DIE, NP_o, REL_obj_VERB)), lambda np_s, die, np_o, verb, su_idx, obj_idx: (su_idx, get_top(np_o)[0]))
]

rules = AbsRule.from_list(list(zip(*annotated_rules))[0])
# rules = AbsRule.from_list([
#         (S,         (CTRL,)),
#         (CTRL,      (NP_s, TV_su_ctrl, NP_o, VC)),
#         (CTRL,      (NP_s, TV_obj_ctrl, NP_o, VC)),
#         (VC,        (TE, INF)),
#         (INF,       (ITV_inf,)),
#         (VC,        (INF_tv, TE)),
#         (VC,        (NP_o2, TE, INF_ctrl, VC)),
#         (NP_s,      (NP_s, DIE, NP_o, REL_su_VERB)),
#         (NP_s,      (NP_s, DIE, NP_o, REL_obj_VERB))
#     ])


grammar = AbsGrammar(rules)
trees = grammar.generate(S, 4, True)


def fst(x, y):
        return x


def snd(x, y):
        return y

span_rules = {AbsRule(lhs, rhs): lam for ((lhs, rhs), lam) in annotated_rules}

span_constants = {TV_su_ctrl: fst, TV_obj_ctrl: snd,
                  ITV_inf: fst, INF_ctrl: fst, REL_su_VERB: fst,
                  REL_obj_VERB: snd, INF_tv: fst}

from ..control_spans.span_realization import abstree_to_labeledtree, labeledtree_to_verbreltree, get_rule
from pprint import pprint
abstree = trees[0]
labtree = abstree_to_labeledtree(abstree, set([NP_s, NP_o, NP_o2]),
                                 set([TV_su_ctrl, TV_obj_ctrl, ITV_inf,INF_ctrl, REL_su_VERB, REL_obj_VERB,INF_tv]),
                                 (n for n in range(1,20)),
                                 (n for n in range(1,20)))


# verbreltree = labeledtree_to_verbreltree(labtree, None, None, span_rules, span_constants)