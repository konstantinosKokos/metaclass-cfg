from dataclasses import dataclass
from itertools import product
from typing import Union


@dataclass
class Category:
    surface:    str


class CategoryMeta(type):
    _constants = []

    def __new__(mcs, name) -> type:
        return super().__new__(mcs, name, (Category,), {})

    @property
    def constants(cls):
        return cls._constants

    @constants.setter
    def constants(cls, values: list[str]):
        cls._constants = list(map(cls, values))

    @classmethod
    def from_list(mcs, names: list[str]) -> list[type]:
        return [CategoryMeta.__new__(mcs, name) for name in names]


AbsTree = Union[CategoryMeta,   tuple[CategoryMeta, tuple['AbsTree', ...]]]
SynTree = Union[Category,       tuple[CategoryMeta, tuple['SynTree', ...]]]


def realizable(tree: AbsTree) -> bool:
    if isinstance(tree, CategoryMeta):
        return len(tree.constants) > 0
    if isinstance(tree, tuple):
        return all(map(realizable, tree[1]))


def realize_tree(tree: AbsTree) -> list[SynTree]:
    if isinstance(tree, CategoryMeta):
        return tree.constants
    options = tuple(map(realize_tree, tree[1]))
    return [(tree[0], opt) for opt in product(*options)]


def realize_trees(trees: list[AbsTree]) -> list[SynTree]:
    return [real for tree in trees for real in realize_tree(tree)]


def surface_tree(tree: SynTree) -> str:
    if isinstance(tree, Category):
        return tree.surface
    return ' '.join(tuple(map(surface_tree, tree[1])))


Rules = tuple[CategoryMeta, list[tuple[CategoryMeta, ...]]]


@dataclass
class Grammar:
    rules: list[Rules]

    def generate(self, goal: CategoryMeta, depth: int, return_empty: bool = True) -> list[AbsTree]:
        trees = self.induction([goal], depth + 1)
        return trees if return_empty else list(filter(realizable, trees))

    def induction(self, options: list[AbsTree], depth: int) -> list[AbsTree]:
        if depth == 0:
            return []
        return options + self.induction(self.expand_options(options), depth - 1)

    def expand_category(self, goal: CategoryMeta) -> list[tuple[CategoryMeta, ...]]:
        return [rhs for lhs, rhss in self.rules if lhs == goal for rhs in rhss]

    def expand_tree(self, tree: AbsTree) -> list[AbsTree]:
        if isinstance(tree, CategoryMeta):
            return [(tree, rhs) for rhs in self.expand_category(tree)]
        branch_options = tuple(map(lambda branch: self.expand_tree(branch) + [branch], tree[1]))
        ret = [(tree[0], p) for p in product(*branch_options)]
        return [r for r in ret if r != tree]

    def expand_options(self, options: list[AbsTree]) -> list[AbsTree]:
        return [expand for option in options for expand in self.expand_tree(option)]

    @staticmethod
    def realize(trees: list[AbsTree]) -> list[SynTree]:
        return realize_trees(trees)
