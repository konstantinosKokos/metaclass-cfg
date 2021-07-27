from ...mcfg import CategoryMeta, Tree, AbsTree, AbsRule
from typing import Union, Iterator
from typing import Optional as Maybe


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


def get_rule(category: CategoryMeta, children: tuple[LabeledTree, ...]) -> AbsRule
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


def labeledtree_to_surface(
        tree: LabeledTree, surface_rules: SurfaceRule, np_labels: list[int], vp_labels: list[int]) \
            -> list[tuple[tuple[list[int], list[int]], CategoryMeta]]:
    # todo.

    def add_to_inheritance(_inheritance: list[int], new_idx: Maybe[int]) -> list[int]:
        return _inheritance if new_idx is None else _inheritance + [new_idx]

    if len(tree) == 3:
        np_idx, vp_idx, category = tree
        return [(add_to_inheritance(np_labels, np_idx), add_to_inheritance(vp_labels, vp_idx), category)]
    (np_idx, vp_idx, category), children = tree
    np_labels = add_to_inheritance(np_labels, np_idx)
    vp_labels = add_to_inheritance(vp_labels, vp_idx)
    abs_rule = get_rule(category, children)
    surf_rule = surface_rules[abs_rule]
    # fucked up shit
    children_labels = tuple(map(lambda c: labeledtree_to_surface(c, surface_rules, np_labels, vp_labels), children))
    ret = [[] for _ in len(surf_rule)]
    for result_crd in surf_rule:
        for child_id, child_crd in result_crd:
            ret.extend(children_labels[child_id])
    # for child_np_labels, child_vp_labels, child_categories in children_labels:
