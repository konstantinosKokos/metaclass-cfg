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

"""
    S(XYZ) -> PREF(X) EMB(Y, Z)
    EMB(X, Y) -> NP_s(X) ITV_inf_action(Y)
    EMB(XY, Z) -> NP_s(X) NP_o(Y) TV_inf_action(Z)
    EMB(XY, ZU) -> NP_s(X), TV_inf_sense(Z), EMB(Y, U)
    EMB(XY, ZU) -> NP_s(X) NP_s2(Y) TV_inf_ctrl(Z) VC(U)
    VC(XY) -> TE(X) ITV_inf_action(Y)
"""

""" TODO: Add declarative forms of the embedded clauses, so we can experiment with it. 
This is only possible with sense verbs, not in general. """

from ...mcfg import CategoryMeta, AbsRule, AbsGrammar
from typing import Optional as Maybe
from .span_realization import exhaust_grammar
from .lexicon import Lexicon
from random import seed as set_seed
from random import shuffle
import json

# Categories
S = CategoryMeta('S')
PREF = CategoryMeta('PREF')
EMB = CategoryMeta('EMB', 2)
TE = CategoryMeta('TE')

NP = CategoryMeta('NP')
NP_s = CategoryMeta('NP_s')
NP_s2 = CategoryMeta('NP_s2')
NP_o = CategoryMeta('NP_o')

INF_itv = CategoryMeta('INF_itv')
INF_tv = CategoryMeta('INF_tv')

IPP_itv = CategoryMeta('IPP_itv')
IPP_tv = CategoryMeta('IPP_tv')
IPP_itv_te = CategoryMeta('IPP_itv_te')

INF_su_ctrl = CategoryMeta('INF_su_ctrl')
INF_obj_ctrl = CategoryMeta('INF_obj_ctrl')

VC = CategoryMeta('VC')


annotated_rules = [
        ((S,            (PREF, EMB)),
         (dict(),       (False, False)),
         ([(0, 0), (1, 0), (1, 1)],)),
        # EMB <- ...
        # Intransitive case
        ((EMB,          (NP_s, INF_itv)),
         ({1: 0},       (False, False)),
         ([(0, 0)], [(1, 0)])),
        # Intransitive case + IPP
        ((EMB,          (NP_s, IPP_itv, INF_itv)),
         ({1: 0,
           2: 0},       (False, False, False)),
         ([(0, 0)], [(1, 0), (2, 0)])),
        ((EMB,          (NP_s, IPP_itv, IPP_itv, INF_itv)),
         ({1: 0,
           2: 0,
           3: 0},       (False, False, False, False)),
         ([(0, 0)], [(1, 0), (2, 0), (3, 0)])),
        # Intransitive case + IPP (te)
        ((EMB,          (NP_s, IPP_itv_te, TE, INF_itv)),
         ({1: 0,
           3: 0},       (False, False, False, False)),
         ([(0, 0)], [(1, 0), (2, 0), (3, 0)])),
        ((EMB,          (NP_s, IPP_itv_te, TE, IPP_itv_te, TE, INF_itv)),
         ({1: 0,
           3: 0,
           5: 0},       (False, False, False, False, False, False)),
         ([(0, 0)], [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0)])),
        # Transitive case
        ((EMB,          (NP_s, NP_o, INF_tv)),
         ({2: 0},       (False, False, False)),
         ([(0, 0), (1, 0)], [(2, 0)])),
        # Transitive case + IPP
        ((EMB,          (NP_s, NP_o, IPP_itv, INF_tv)),
         ({2: 0,
           3: 0},       (False, False, False, False)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0)])),
        ((EMB,          (NP_s, NP_o, IPP_itv, IPP_itv, INF_tv)),
         ({2: 0,
           3: 0,
           4: 0},       (False, False, False, False, False)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0), (4, 0)])),
        # # Transitive case + IPP (te)
        ((EMB,          (NP_s, NP_o, IPP_itv_te, TE, INF_tv)),
         ({2: 0,
           4: 0},       (False, False, False, False, False)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0), (4, 0)])),
        ((EMB,          (NP_s, NP_o, IPP_itv_te, TE, IPP_itv_te, TE, INF_tv)),
         ({2: 0,
           4: 0,
           6: 0},       (False, False, False, False, False, False, False)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0)])),
        # EMB recursion
        ((EMB,          (NP_s, IPP_tv, EMB)),
         ({1: 0},       (False, False, False)),
         ([(0, 0), (2, 0)], [(1, 0), (2, 1)])),
        # IPP (te) case with word order variation (the 'third construction' of Augustinus)
        # It's a variation on the transitive case with an IPP (te) verb, allowing the verb cluster to break open.
        ((EMB,          (NP_s, IPP_itv_te, NP_o, TE, INF_tv)),
         ({1: 0,
           4: 0},       (False, False, False, False, False)),
         ([(0, 0), (1, 0), (2, 0)], [(3, 0), (4, 0)])),
        # # Inserting control verbs
        ((EMB,          (NP_s, NP_s2, INF_su_ctrl, VC)),
         ({2: 0},       (False, False, False, 0)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0)])),
        ((EMB,          (NP_s, NP_s2, INF_obj_ctrl, VC)),
         ({2: 0},       (False, False, False, 1)),
         ([(0, 0), (1, 0)], [(2, 0), (3, 0)])),
        # VC <- ...
        ((VC,           (TE, INF_itv)),
         ({1: None},    (False, False)),
         ([(0, 0), (1, 0)],)),
        # TODO: Do we want to add recursion here, for the real mindf*ck?
        # NP <- ...
        ((NP_s,             (NP,)),
         (dict(),           (False,)),
         ([(0, 0)],)),
        ((NP_o,             (NP,)),
         (dict(),           (False,)),
         ([(0, 0)],)),
        ((NP_s2,            (NP,)),
         (dict(),           (False,)),
         ([(0, 0)],)),
]

n_candidates = {NP_s, NP_o, NP_s2}
# n_candidates = {NP_s, NP_o}
v_candidates = {INF_itv, INF_tv, IPP_itv, IPP_tv, IPP_itv_te, INF_su_ctrl, INF_obj_ctrl}
exclude_candidates = {TE}


def make_grammar(excluded_rules: set[int]) -> tuple[AbsGrammar, dict[AbsRule, ...], dict[AbsRule, ...]]:
    subrules = [r for i, r in enumerate(annotated_rules) if i not in excluded_rules]
    return (AbsGrammar(AbsRule.from_list([r[0] for r in subrules])),
            {AbsRule(lhs, rhs): matching_rule for ((lhs, rhs), matching_rule, _) in subrules},
            {AbsRule(lhs, rhs): surf_rule for ((lhs, rhs), _, surf_rule) in subrules})


full_grammar, matching_rules, surf_rules = make_grammar(set())


def set_constants(nouns: list[str], su_verbs_inf: list[str], obj_verbs_inf: list[str],
                  inf_ivs: list[str], inf_tvs: list[str], ipp_itvs: list[str], ipp_tvs: list[str],
                  ipp_itvs_te: list[str]):
    NP.constants = nouns

    INF_su_ctrl.constants = su_verbs_inf
    INF_obj_ctrl.constants = obj_verbs_inf
    INF_itv.constants = inf_ivs
    INF_tv.constants = [tv for tv in inf_tvs if tv not in ipp_tvs]
    IPP_itv.constants = ipp_itvs
    IPP_tv.constants = ipp_tvs
    IPP_itv_te.constants = ipp_itvs_te
    PREF.constants = ['Iemand ziet']
    TE.constants = ['te']


def get_grammar(max_depth: int, sample: Maybe[int], min_depth: int = 0, grammar: AbsGrammar = full_grammar):
    return exhaust_grammar(grammar, S, surf_rules, matching_rules, max_depth, n_candidates,
                           v_candidates, sample, min_depth, exclude_candidates)


def setup_grammar():
    # Init lexicon
    all_nouns = Lexicon.de_nouns()
    su_verbs_inf = Lexicon.sub_control_verbs_inf()
    obj_verbs_inf = Lexicon.obj_control_verbs_inf()
    inf_ivs = Lexicon.infinitive_verbs()
    inf_tvs = Lexicon.vos()
    ipp_itvs = Lexicon.ipp_itvs()
    ipp_tvs = Lexicon.ipp_tvs()
    ipp_itvs_te = Lexicon.ipp_itvs_te()

    seed = 2353290823
    set_seed(seed)
    shuffle(all_nouns)
    shuffle(su_verbs_inf)
    shuffle(obj_verbs_inf)
    shuffle(inf_ivs)
    shuffle(inf_tvs)
    shuffle(ipp_itvs)
    shuffle(ipp_tvs)
    shuffle(ipp_itvs_te)

    noun_l, noun_r = 0, 100
    su_verb_l, su_verb_r = 0, 9
    obj_verb_l, obj_verb_r = 0, 33
    min_depth, max_depth = 2, 8
    num_samples = 1
    set_constants(nouns=all_nouns[noun_l:noun_r],
                  su_verbs_inf=su_verbs_inf[su_verb_l:su_verb_r],
                  obj_verbs_inf=obj_verbs_inf[obj_verb_l:obj_verb_r],
                  inf_ivs=inf_ivs,
                  inf_tvs=inf_tvs,
                  ipp_itvs=ipp_itvs,
                  ipp_tvs=ipp_tvs,
                  ipp_itvs_te=ipp_itvs_te)
    grammar = full_grammar
    results = {depth: {str(tree): (matching, [str(surf) for surf in surfaces])
               for tree, (matching, surfaces) in trees.items()}
               for depth, trees in get_grammar(max_depth, num_samples, min_depth=min_depth,
               grammar=grammar).items()}
    return grammar, results


def extract_sentence(inp: str) -> str:
    return ' '.join([i[2] for i in eval(inp)])


def extract_sentences(results: dict) -> list[str]:
    return [s for (m, surfs) in results.values() for s in list(map(extract_sentence, surfs))]


def get_sentences(results: dict):
    return {d: extract_sentences(results[d]) for d in results}


def main(gen_file: str):
    with open(gen_file, 'r') as f:
        experiment = json.load(f)['cluster']

    all_nouns = Lexicon.de_nouns()
    su_verbs_inf = Lexicon.sub_control_verbs_inf()
    obj_verbs_inf = Lexicon.obj_control_verbs_inf()
    inf_ivs = Lexicon.infinitive_verbs()
    inf_tvs = Lexicon.vos()
    ipp_itvs = Lexicon.ipp_itvs()
    ipp_tvs = Lexicon.ipp_tvs()
    ipp_itvs_te = Lexicon.ipp_itvs_te()

    seed = experiment["seed"]
    set_seed(seed)
    shuffle(all_nouns)
    shuffle(su_verbs_inf)
    shuffle(obj_verbs_inf)
    shuffle(inf_ivs)
    shuffle(inf_tvs)
    shuffle(ipp_itvs)
    shuffle(ipp_tvs)
    shuffle(ipp_itvs_te)

    min_depth, max_depth = experiment['depth']
    num_samples = experiment['samples']

    set_constants(nouns=all_nouns,
                  su_verbs_inf=su_verbs_inf,
                  obj_verbs_inf=obj_verbs_inf,
                  inf_ivs=inf_ivs,
                  inf_tvs=inf_tvs,
                  ipp_itvs=ipp_itvs,
                  ipp_tvs=ipp_tvs,
                  ipp_itvs_te=ipp_itvs_te)

    result = {depth: {str(tree): (matching, [str(surf) for surf in surfaces])
                      for tree, (matching, surfaces) in trees.items()}
              for depth, trees in get_grammar(max_depth, num_samples,
                                              min_depth=min_depth, grammar=full_grammar).items()}
    with open(f'./grammars/cluster_{seed}.json', 'w') as out_file:
        json.dump(result, out_file, indent=4)
