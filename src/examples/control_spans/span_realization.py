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
# fn([NP_s, DIE, NP_o, REL_su_VERB, TV_su_ctrl, NP_o, INF_tv, TE]) = DATAAAA

SpanRealization = list[tuple[list[int], list[int], tuple[int, int]]]
Realized = list[tuple[list[int], list[int], str]]


def project_tree(tree: LabeledTree) -> list[CategoryMeta]:
    if len(tree) == 3:
        return [tree[2]]
    _, children = tree
    return sum([project_tree(c) for c in children], [])


def get_choices(leaves: list[CategoryMeta]) -> list[list[Category]]:
    constants = [leaf.constants for leaf in leaves]
    return list(map(list, product(*constants)))


def realize_span(leaves: list[Category], span_realization: SpanRealization) -> Realized:
    return [(nps, vps, leaves[idx][coord]) for nps, vps, (idx, coord) in span_realization]


def labeled_tree_to_realization(
        tree: LabeledTree, surface_rules: SurfaceRule, np_labels: list[int], vp_labels: list[int],
        offset: int = 0) -> tuple[int, list[SpanRealization]]:

    def _f(_tree: LabeledTree, _offset: int) -> tuple[int, list[SpanRealization]]:
        return labeled_tree_to_realization(_tree, surface_rules, np_labels, vp_labels, _offset)

    def add_to_inheritance(_inheritance: list[int], new_idx: Maybe[int]) -> list[int]:
        return _inheritance if new_idx is None else _inheritance + [new_idx]

    if len(tree) == 3:
        np_idx, vp_idx, category = tree
        _np_labels, _vp_labels = add_to_inheritance(np_labels, np_idx), add_to_inheritance(vp_labels, vp_idx)
        return offset + 1, [[(np_labels, _vp_labels, (offset, i))] for i in range(category.arity)]

    (np_idx, vp_idx, category), children = tree
    np_labels = add_to_inheritance(np_labels, np_idx)
    vp_labels = add_to_inheritance(vp_labels, vp_idx)
    abs_rule = get_rule(category, children)
    surf_rule: tuple[list[tuple[int, int]], ...] = surface_rules[abs_rule]
    branch_realizations: list[list[SpanRealization]] = []
    for child in children:
        offset, branch_realization = _f(child, offset)
        branch_realizations.append(branch_realization)
    return offset, [sum([branch_realizations[idx][crd] for idx, crd in res_crd], []) for res_crd in surf_rule]
