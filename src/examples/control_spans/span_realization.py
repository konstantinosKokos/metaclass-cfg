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




def get_rule(tree: LabeledTree) -> Union[CategoryMeta, AbsRule]:
    # if isinstance(tree, CategoryMeta):
    if len(tree) == 3:
        return tree[2]
    # if isinstance(tree, tuple):
    if len(tree) == 2:
        parent, children = tree
        return AbsRule(parent[2], tuple([get_top(c)[2] for c in children]))




def labeledtree_to_verbreltree(tree: LabeledTree, subj_idx: Maybe[int], obj_idx: Maybe[int],
                               span_rules, span_constants) -> VerbRelTree:
    def _f(_tree: LabeledTree, _su_idx, _obj_idx):
        return labeledtree_to_verbreltree(_tree, _su_idx, _obj_idx, span_rules, span_constants)

    def assign_id(node: LabeledNode) -> VerbRelNode:
        if node[1]:
            return (node[1], span_constants[node[2]](subj_idx, obj_idx)), node[2]
        else:
            return None, node[2]

    # if isinstance(tree, CategoryMeta):
    if len(tree) == 3:
        return assign_id(tree)
    # if isinstance(tree, tuple):
    if len(tree) == 2:
        parent, children = tree
        new_subj_idx, new_obj_idx = span_rules[get_rule(tree)](*children, subj_idx, obj_idx)
        return assign_id(parent), tuple(map(lambda c: _f(c, new_subj_idx, new_obj_idx), children))




# def fmap_depthfirst(tree: Tree, node_map) -> Tree:
#     if isinstance(tree, Node):
#         return node_map(tree)
#     if isinstance(tree, tuple):
#         parent, children = tree
#         return node_map(parent), tuple(map(lambda c: fmap_depthfirst(c, node_map), children))
#

def extract_verb_rels(tree: VerbRelTree) -> list[tuple[int, int]]:
    # A VerbRelTree always has length 2
    if isinstance(tree[1], CategoryMeta):
        return [tree[0]] if tree[0] not is None else []
    if isinstance(tree[1], tuple):
        pass