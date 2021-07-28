from ...mcfg import Category, CategoryMeta, Tree, AbsTree, AbsRule
from typing import Union, Iterator
from typing import Optional as Maybe
from itertools import product

LabeledNode = tuple[Maybe[int], Maybe[int],  CategoryMeta]
LabeledTree = Tree[LabeledNode]
Matching = dict[int, int]
MatchingRule = dict[AbsRule, tuple[dict[int, Maybe[int]], tuple[Union[bool, int], ...]]]
SurfaceRule = dict[AbsRule, tuple[list[tuple[int, int]], ...]]


def abstree_to_labeledtree(tree: AbsTree, n_candidates: set[CategoryMeta], v_candidates: set[CategoryMeta],
                           n_counter: Iterator[int], v_counter: Iterator[int]) -> LabeledTree:
    def _f(_tree: AbsTree):
        return abstree_to_labeledtree(_tree, n_candidates, v_candidates, n_counter, v_counter)

    def assign_node(category: CategoryMeta) -> LabeledNode:
        if category in n_candidates:
            return next(n_counter), None, category
        if category in v_candidates:
            return None, next(v_counter), category
        return None, None, category

    if isinstance(tree, CategoryMeta):
        return assign_node(tree)
    if isinstance(tree, tuple):
        parent, children = tree
        return assign_node(parent), tuple(map(_f, children))


def get_top(_tree: LabeledTree) -> LabeledNode:
    return _tree if len(_tree) == 3 else _tree[0]


def get_rule(category: CategoryMeta, children: tuple[LabeledTree, ...]) -> AbsRule:
    children_categories = tuple(map(lambda c: get_top(c)[-1], children))
    return AbsRule(category, children_categories)


def get_matchings(tree: LabeledTree, matching_rules: MatchingRule, inheritance: Maybe[int] = None) -> Matching:
    if len(tree) == 3:
        return {}
    (_, _, category), children = tree
    abs_rule = get_rule(category, children)
    branch_matches, inheritances = matching_rules[abs_rule]
    ret = {children[k][1]: get_top(children[v])[0] if v is not None else inheritance
           for k, v in branch_matches.items()}
    for child, inh in zip(children, inheritances):
        ret.update(get_matchings(
            child,
            matching_rules,
            get_top(children[inh])[0] if isinstance(inh, int) else inheritance if inh else None))
    return ret


# ((None, None, <class 'src.mcfg.S'>),
#  (((None, None, <class 'src.mcfg.CTRL'>),
#    (((0, None, <class 'src.mcfg.NP_s'>),
#      ((1, None, <class 'src.mcfg.NP_s'>),
#       (None, None, <class 'src.mcfg.DIE'>),
#       (2, None, <class 'src.mcfg.NP_o'>),
#       (None, 0, <class 'src.mcfg.REL_su_VERB'>))),
#     (None, 1, <class 'src.mcfg.TV_su_ctrl'>),
#     (3, None, <class 'src.mcfg.NP_o'>),
#     ((None, None, <class 'src.mcfg.VC'>),
#      ((None, 2, <class 'src.mcfg.INF_tv'>),
#       (None, None, <class 'src.mcfg.TE'>))))),))

# {1: 0, 0: 1, 2: 0}


SpanSurface = tuple[list[list[int]], list[list[int]], list[list[str]]]

# A yield is a tuple (the arity) of results, each of which encodes one of the resulting elements in the tuple.
# Each element contains the NP spans, VP spans, and a list of concrete surface forms.
# Each NP Span object is a list of lists of int, indicating that at each position of a surface form, it belongs to a
# number of NP's. Likewise, each position in the surface form (note that this in itself could contain multiple words)
# belongs to a number of VP's. The list of concrete surface forms is a list of options for concrete forms, where each
# form is a list of strings (each of which has a surface string which we later use to generate actual spans).
# Note: we use str instead of Category because we require the actual string tuples, which are hidden in the surface of
# each category.
# NPSpan = list[list[int]]
# VPSpan = list[list[int]]
# SurfaceSpan = list[list[str]]
# Yield = tuple[tuple[NPSpan, VPSpan, SurfaceSpan]]
# Example: NP_s has a list of three constants, and arity one, so output is
# (([[0, 1]], [[]] , [[NP_s(de man), NP_s(de vrouw), NP_s(het kind)]]),)
# Example 2: For a VP -> NP Verb it would be
# (([[0, 1], []], [[], [1]] , [[NP_s(de man), NP_s(de vrouw), NP_s(het kind)], [V(ziet), V(hoort)]]),)
# Example 3: For a INF_tv with pairs of constants [('bier', 'drinken'), ('pizza', 'eten')] we should get
# (([[0, 1]] , [[]] , [['bier', 'pizza']]), ([[]], [[1]] , [['drinken', 'eten']]))
def labeledtree_to_surface(
        tree: LabeledTree, surface_rules: SurfaceRule, np_labels: list[int], vp_labels: list[int]) \
            -> SpanSurface:
    def add_to_inheritance(_inheritance: list[int], new_idx: Maybe[int]) -> list[int]:
        return _inheritance if new_idx is None else _inheritance + [new_idx]

    if len(tree) == 3:
        np_idx, vp_idx, category = tree
        _np_labels, _vp_labels = [add_to_inheritance(np_labels, np_idx)], [add_to_inheritance(vp_labels, vp_idx)]
        return tuple(map(lambda surf_options: (_np_labels, _vp_labels, [list(surf_options)]), zip(*category.constants)))

    (np_idx, vp_idx, category), children = tree
    np_labels = add_to_inheritance(np_labels, np_idx)
    vp_labels = add_to_inheritance(vp_labels, vp_idx)
    abs_rule = get_rule(category, children)
    surf_rule: tuple[list[tuple[int, int]]] = surface_rules[abs_rule]
    children_labels = tuple(map(lambda c: labeledtree_to_surface(c, surface_rules, np_labels, vp_labels), children))

    def construct_surface_el(el: list[tuple[int, int]]) -> tuple[list[list[int]], list[list[int]], list[list[str]]]:
        span_surfs = list(zip(*[children_labels[c_idx][c_coord] for c_idx, c_coord in el]))
        return sum(span_surfs[0], []), sum(span_surfs[1], []), sum(span_surfs[2], [])

    return tuple(map(construct_surface_el, surf_rule))


# functions that map a SpanSurface to concrete data for evaluation.
def get_span(idx: int, surf: str) -> list[int]:
    return len(surf.split()) * [idx]


def get_span_ids(spans: list[list[int]]):
    return set([n for s in spans for n in s])


def span_surface_example_to_data(spans: list[list[int]], span_idx: int, surface: tuple[str]):
    all_spans = []
    for span, surf in zip(spans, surface):
        cur_idx = span_idx if span_idx in span else None
        cur_span = get_span(cur_idx, surf)
        all_spans.append(cur_span)
    return [n for s in all_spans for n in s]


def span_surface_to_data(span_surf: SpanSurface, matchings: Matching, verb_idx: int):
    np_spans, vp_spans, surfs = span_surf
    surf_options = list(product(*surfs))
    all_results = []
    for surf_opt in surf_options:
        result = [span_surface_example_to_data(np_spans, i, surf_opt) for i in get_span_ids(np_spans)], ' '.join(surf_opt)
        all_results.append(result)
    return all_results