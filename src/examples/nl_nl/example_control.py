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
from ...mcfg import CategoryMeta, AbsRule, AbsGrammar
from typing import Optional as Maybe
from .span_realization import Matching, Realized, exhaust_grammar
from .lexicon import Lexicon
from random import seed as set_seed
from random import shuffle
import json


# Categories
CTRL = CategoryMeta('CTRL')

VC = CategoryMeta('VC', 2)
INF = CategoryMeta('INF')
INF_tv = CategoryMeta('INF_tv')

TE = CategoryMeta('TE')

NP = CategoryMeta('NP')
NP_s = CategoryMeta('NP_s')
NP_o = CategoryMeta('NP_o')
NP_o2 = CategoryMeta('NP_o2')

TV_su_ctrl = CategoryMeta('TV_su_ctrl')
TV_obj_ctrl = CategoryMeta('TV_obj_ctrl')
INF_su_ctrl = CategoryMeta('INF_su_ctrl')
INF_obj_ctrl = CategoryMeta('INF_obj_ctrl')
INF_itv = CategoryMeta('ITV_inf')
AUX_subj = CategoryMeta('AUX_subj')
AUX_obj = CategoryMeta('AUX_obj')
DIE = CategoryMeta('DIE')
REL_su_VERB = CategoryMeta('REL_su_VERB')
REL_obj_VERB = CategoryMeta('REL_obj_VERB')

# Constants
AUX_subj.constants = ['laten']
AUX_obj.constants = ['doen']

REL_su_VERB.constants = ['helpt', 'bijstaat']
REL_obj_VERB.constants = ['negeert', 'verpleegt']

"""
    S(X) -> CTRL(X)
    CTRL(XYZUV) -> NP_s(X) TV(Y) NP_o(Z) VC(U, V)
    CTRL(XYZUVW) -> NP_s(X) TV(Y) NP_o(Z) AUX(V) VC(U, W)
    VC(XY, Z) -> INF_tv(X, Z), TE(Y) 
    VC(XY, ZUV) -> NP_o2(X) TE(Y) INF_ctrl(Z) VC(U, V)
    VC(XYZ, UVW) -> NP_o2(X) TE(Y) INF_ctrl(U) AUX(Z) VC(V, W) 
    NP_s(XYZU) -> NP_s(X) DIE(Y) NP_o(Z) REL(U)

 """

annotated_rules = [
        ((CTRL,             (NP_s, TV_su_ctrl, NP_o, VC)),
         ({1: 0},           (False, False, False, 0)),
         ([(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],)),
        ((CTRL,             (NP_s, TV_obj_ctrl, NP_o, VC)),
         ({1: 0},           (False, False, False, 2)),
         ([(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],)),
        ((CTRL,             (NP_s, TV_su_ctrl, NP_o, AUX_subj, VC)),
         ({1: 0,
           3: 0},           (False, False, False, False, 2)),
         ([(0, 0), (1, 0), (2, 0), (4, 0), (3, 0), (4, 1)],)),
        ((CTRL,             (NP_s, TV_su_ctrl, NP_o2, NP_o, AUX_subj, VC)),
         ({1: 0,
           4: 0},           (False, False, False, False, False, 3)),
         ([(0, 0), (1, 0), (2, 0), (3, 0), (5, 0), (4, 0), (5, 1)],)),
        ((CTRL,             (NP_s, TV_obj_ctrl, NP_o, AUX_obj, VC)),
         ({1: 0,
           3: 2},           (False, False, False, False, 0)),
         ([(0, 0), (1, 0), (2, 0), (4, 0), (3, 0), (4, 1)],)),
        ((CTRL,             (NP_s, TV_obj_ctrl, NP_o2, NP_o, AUX_obj, VC)),
         ({1: 0,
           4: 3},           (False, False, False, False, False, 0)),
         ([(0, 0), (1, 0), (2, 0), (3, 0), (5, 0), (4, 0), (5, 1)],)),
        ((VC,               (TE, INF_itv)),
         ({1: None},        (False, False)),
         ([(0, 0)], [(1, 0)])),
        ((VC,               (TE, INF_tv, NP)),
         ({1: None},        (False, False, False)),
         ([(2, 0), (0, 0)], [(1, 0)])),
        ((VC,               (NP_o2, TE, INF_su_ctrl, VC)),
         ({2: None},        (False, False, False, True)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0), (3, 1)])),
        ((VC,               (NP_o2, TE, INF_obj_ctrl, VC)),
         ({2: None},        (False, False, False, 0)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0), (3, 1)])),
        ((VC,               (NP_o2, TE, INF_su_ctrl, AUX_subj, VC)),
         ({2: None,
           3: None},        (False, False, False, False, True)),
         ([(0, 0), (1, 0), (3, 0)], [(2, 0), (4, 0), (4, 1)])),
        ((VC,               (NP_o2, TE, INF_obj_ctrl, AUX_obj, VC)),
         ({2: None,
           3: None},        (False, False, False, False, 0)),
         ([(0, 0), (1, 0), (3, 0)], [(2, 0), (4, 0), (4, 1)])),
        ((NP_s,             (NP,)),
         (dict(),           (False,)),
         ([(0, 0)],)),
        ((NP_o,             (NP,)),
         (dict(),           (False,)),
         ([(0, 0)],)),
        ((NP_o2,            (NP,)),
         (dict(),           (False,)),
         ([(0, 0)],)),
        # ((NP,               (NP, DIE, NP, REL_su_VERB)),
        #  ({3: 0},           (False, False, False, False)),
        #  ([(0, 0), (1, 0), (2, 0), (3, 0)],)),
        # ((NP,               (NP, DIE, NP, REL_obj_VERB)),
        #  ({3: 2},           (False, False, False, False)),
        #  ([(0, 0), (1, 0), (2, 0), (3, 0)],))
]

n_candidates = {NP_s, NP_o, NP_o2, NP}
v_candidates = {TV_su_ctrl, TV_obj_ctrl, INF_itv, INF_su_ctrl, INF_obj_ctrl, REL_su_VERB,
                REL_obj_VERB, INF_tv, AUX_subj, AUX_obj}

grammar = AbsGrammar(AbsRule.from_list([r[0] for r in annotated_rules]))

matching_rules = {AbsRule(lhs, rhs): matching_rule for ((lhs, rhs), matching_rule, _) in annotated_rules}
surf_rules = {AbsRule(lhs, rhs): surf_rule for ((lhs, rhs), _, surf_rule) in annotated_rules}

exclude_candidates = {DIE, TE, AUX_subj, AUX_obj}


def set_constants(nouns: list[str], su_verbs: list[str], su_verbs_inf: list[str],
                  obj_verbs: list[str], obj_verbs_inf: list[str], inf_ivs: list[str], inf_tvs: list[tuple[str, str]]):
    NP.constants = nouns

    TV_su_ctrl.constants = su_verbs
    TV_obj_ctrl.constants = obj_verbs
    INF_su_ctrl.constants = su_verbs_inf
    INF_obj_ctrl.constants = obj_verbs_inf
    INF_itv.constants = inf_ivs
    INF_tv.constants = inf_tvs
    DIE.constants = ['die']
    TE.constants = ['te']


def get_grammar(max_depth: int, sample: Maybe[int], min_depth: int = 0):
    return exhaust_grammar(grammar, CTRL, surf_rules, matching_rules, max_depth, n_candidates,
                           v_candidates, sample, min_depth, exclude_candidates)


def json_string(matching: Matching, surfaces: list[Realized]):
    return json.dumps({'matching': matching, 'surfaces': surfaces})


def main(max_depth: int, out_fn: str, noun_idxs: tuple[int, int], su_verb_idxs: tuple[int, int],
         obj_verb_idxs: tuple[int, int], num_samples: Maybe[int] = None, seed: Maybe[int] = None,
         min_depth: int = 0):
    all_nouns = Lexicon.de_nouns()
    su_verbs = Lexicon.sub_control_verbs_present()
    su_verbs_inf = Lexicon.sub_control_verbs_inf()
    obj_verbs = Lexicon.obj_control_verbs_present()
    obj_verbs_inf = Lexicon.obj_control_verbs_inf()
    inf_ivs = Lexicon.infinitive_verbs()
    inf_tvs = Lexicon.vos()

    if seed is not None:
        set_seed(seed)
        shuffle(all_nouns)
        shuffle(su_verbs)
        shuffle(su_verbs_inf)
        shuffle(obj_verbs)
        shuffle(obj_verbs_inf)
        shuffle(inf_ivs)
        shuffle(inf_tvs)

    (noun_l, noun_r) = noun_idxs
    (su_verb_l, su_verb_r) = su_verb_idxs
    (obj_verb_l, obj_verb_r) = obj_verb_idxs
    set_constants(nouns=all_nouns[noun_l:noun_r],
                  su_verbs=su_verbs[su_verb_l:su_verb_r],
                  su_verbs_inf=su_verbs_inf[su_verb_l:su_verb_r],
                  obj_verbs=obj_verbs[obj_verb_l:obj_verb_r],
                  obj_verbs_inf=obj_verbs_inf[obj_verb_l:obj_verb_r],
                  inf_ivs=inf_ivs,
                  inf_tvs=inf_tvs)

    if os.path.isfile(out_fn):
        os.remove(out_fn)
    with open(out_fn, 'a') as out_file:
        implemented = {depth: {str(tree): (matching, [str(surf) for surf in surfaces])
                               for tree, (matching, surfaces) in trees.items()}
                       for depth, trees in get_grammar(max_depth, num_samples, min_depth=min_depth).items()}
        json.dump(implemented, out_file, indent=4)
    return implemented
