from ...mcfg import Category, CategoryMeta, Tree, AbsTree, AbsRule, AbsGrammar
from typing import Union, Iterator, Sequence
from typing import Optional as Maybe
from random import choice as choose
from operator import eq
from itertools import product

LabeledNode = tuple[Maybe[int], Maybe[int],  CategoryMeta]
LabeledTree = Tree[LabeledNode]
Matching = dict[int, int]
MatchingRule = dict[AbsRule, tuple[dict[int, Maybe[int]], tuple[Union[bool, int], ...]]]
SurfaceRule = dict[AbsRule, tuple[list[tuple[int, int]], ...]]
SpanRealization = list[tuple[list[int], list[int], tuple[int, int]]]
Realized = list[tuple[list[int], list[int], str]]


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
            get_top(children[inh])[0] if not isinstance(inh, bool) else inheritance if inh else None))
    return ret


def project_tree(tree: LabeledTree) -> list[CategoryMeta]:
    if len(tree) == 3:
        return [tree[2]]
    _, children = tree
    return sum([project_tree(c) for c in children], [])


def has_no_duplicates(realized: Realized, types: list[CategoryMeta], exclude: set[CategoryMeta] = frozenset()) -> bool:
    strs = realized_to_strs(realized)
    non_excluded = [s for t, s in zip(types, strs) if t not in exclude]
    return (not any(map(eq, strs, strs[1:]))) and len(set(non_excluded)) == len(non_excluded)


def realized_to_strs(realized: Realized) -> tuple[str, ...]:
    return tuple(r[2] for r in realized)


def get_choices(
        leaves: list[CategoryMeta],
        realization: SpanRealization,
        exclude: set[CategoryMeta] = frozenset()) -> Iterator[Realized]:
    def rspan(c) -> Realized: return realize_span(c, realization)
    def rtypes(c) -> list[CategoryMeta]: return realize_types(c, realization)
    def ndupes(c) -> bool: return has_no_duplicates(c, rtypes(c), exclude)
    return map(rspan, filter(ndupes, product(*map(lambda cat: cat.constants, leaves))))


def sample_choices(
        leaves: list[CategoryMeta],
        span_realization: SpanRealization,
        n: int,
        exclude: set[CategoryMeta] = frozenset()) -> Iterator[Realized]:
    returned, limit = set(), 0
    while limit := limit + 1 < 1 + n ** 2 and len(returned) < n:
        choice = tuple([choose(cat.constants) for cat in leaves])
        realized, types = realize_span(choice, span_realization), realize_types(choice, span_realization)
        if has_no_duplicates(realized, types, exclude) and (t := realized_to_strs(realized)) not in returned:
            returned.add(t)
            yield realized


def realize_span(leaves: Sequence[Category], span_realization: SpanRealization) -> Realized:
    return [(nps, vps, leaves[idx][coord]) for nps, vps, (idx, coord) in span_realization]


# noinspection PyTypeChecker
def realize_types(leaves: Sequence[Category], span_realization: SpanRealization) -> list[CategoryMeta]:
    return [type(leaves[idx]) for _, _, (idx, _) in span_realization]


def labeled_tree_to_realization(
        tree: LabeledTree, surface_rules: SurfaceRule, np_labels: list[int], vp_labels: list[int],
        offset: int = 0) -> tuple[int, list[SpanRealization]]:

    def _f(_tree: LabeledTree, _offset: int) -> tuple[int, list[SpanRealization]]:
        return labeled_tree_to_realization(_tree, surface_rules, np_labels, vp_labels, _offset)

    def add_to_inheritance(_inheritance: list[int], new_idx: Maybe[int]) -> list[int]:
        return _inheritance if new_idx is None else _inheritance + [new_idx]

    if len(tree) == 3:
        np_idx, vp_idx, category = tree
        np_labels, vp_labels = add_to_inheritance(np_labels, np_idx), add_to_inheritance(vp_labels, vp_idx)
        return offset + 1, [[(np_labels, vp_labels, (offset, i))] for i in range(category.arity)]

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


def exhaust_grammar(
        grammar: AbsGrammar,
        terminal: CategoryMeta,
        surface_rules: dict[AbsRule, tuple[list[tuple[int, int]], ...]],
        matching_rules:  dict[AbsRule, tuple[dict[int, Maybe[int]], tuple[Union[bool, int], ...]]],
        max_depth: int,
        nouns: set[CategoryMeta],
        verbs: set[CategoryMeta],
        sample: Maybe[int] = None,
        min_depth: int = 0,
        exclude_candidates: set[CategoryMeta] = frozenset()) \
        -> dict[int, dict[LabeledTree, tuple[Matching, list[Realized]]]]:
    def choice_fn(leaves: list[CategoryMeta], span_realization: SpanRealization) -> Iterator[Realized]:
        if sample is None:
            return get_choices(leaves, span_realization, exclude_candidates)
        return sample_choices(leaves, span_realization, sample, exclude_candidates)

    def exhaust_tree(_tree: AbsTree) -> tuple[LabeledTree, tuple[Matching, list[Realized]]]:
        labeled_tree = abstree_to_labeledtree(_tree, nouns, verbs, iter(range(999)), iter(range(999)))
        realization = labeled_tree_to_realization(labeled_tree, surface_rules, [], [])[1]
        matching = get_matchings(labeled_tree, matching_rules)
        surfaces = list(choice_fn(project_tree(labeled_tree), realization[0]))
        return labeled_tree, (matching, surfaces)

    def exhaust_depth(_depth: int) -> dict[LabeledTree: tuple[Matching, list[Realized]]]:
        return {k: vs for k, vs in map(exhaust_tree, grammar.generate(terminal, _depth))}

    return {depth: exhaust_depth(depth) for depth in range(min_depth, max_depth)}
