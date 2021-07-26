from ...mcfg import CategoryMeta, Tree, AbsTree
from typing import Union, Iterator
from typing import Optional as Maybe

LabeledNode = tuple[Maybe[int], Maybe[int],  CategoryMeta]
LabeledTree = Tree[LabeledNode]


# ((None, None, <class 'src.mcfg.S'>),                          ([], [], S), ''
#  (((None, None, <class 'src.mcfg.CTRL'>),
#    (((0, None, <class 'src.mcfg.NP_s'>),
#      ((1, None, <class 'src.mcfg.NP_s'>),
#       (None, None, <class 'src.mcfg.DIE'>),
#       (2, None, <class 'src.mcfg.NP_o'>),
#       (None, 0, <class 'src.mcfg.REL_su_VERB'>))),
#     (None, 1, <class 'src.mcfg.TV_SUBJ_ctrl'>),
#     (3, None, <class 'src.mcfg.NP_o'>),
#     ((None, None, <class 'src.mcfg.VC'>),
#      ((None, None, <class 'src.mcfg.INF_tv'>),
#       (None, None, <class 'src.mcfg.TE'>))))),))

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


# def fmap_depthfirst(tree: Tree, node_map) -> Tree:
#     if isinstance(tree, Node):
#         return node_map(tree)
#     if isinstance(tree, tuple):
#         parent, children = tree
#         return node_map(parent), tuple(map(lambda c: fmap_depthfirst(c, node_map), children))
#