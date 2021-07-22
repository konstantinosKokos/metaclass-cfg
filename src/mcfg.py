from typing import Union, Callable
from dataclasses import dataclass
from itertools import product


class Category:
    ...


class CategoryMeta(type):
    _constants = []

    def __new__(mcs, name: str, arity: int = 1) -> type:
        def cls_init(cls, *surface: str) -> None:
            if len(surface) != arity:
                raise TypeError(f'Cannot initialize {cls} of arity {arity} with an {len(surface)}-tuple.')
            cls.surface = surface

        def cls_repr(cls) -> str:
            return f'{name}(surface={str(cls.surface)})'

        def cls_getitem(cls, idx: int) -> str:
            return cls.surface[idx]

        return super().__new__(mcs, name, (Category,), {
            'arity': arity, '__init__': cls_init, '__repr__': cls_repr, '__getitem__': cls_getitem})

    def __init__(cls, _: str, arity: int = 1):
        super(CategoryMeta, cls).__init__(arity)

    @property
    def constants(cls):
        return cls._constants

    @constants.setter
    def constants(cls, values: list[tuple[str, ...]]):
        cls._constants = list(map(cls, values))


Implementation = Callable[[tuple[Category, ...]], Category]


@dataclass
class Rule:
    lhs:            CategoryMeta
    rhs:            tuple[CategoryMeta, ...]
    op:             Implementation

    @classmethod
    def from_list(cls, args: list[tuple[CategoryMeta, tuple[CategoryMeta, ...], Implementation]]) -> list['Rule']:
        return [cls(*arg) for arg in args]


AbsTree = Union[CategoryMeta,
                tuple[CategoryMeta, Implementation, tuple['AbsTree', ...]]]


def realizable(tree: AbsTree) -> bool:
    if isinstance(tree, CategoryMeta):
        return len(tree.constants) > 0
    if isinstance(tree, tuple):
        return all(map(realizable, tree[-1]))


def realize(tree: AbsTree) -> list[Category]:
    if isinstance(tree, CategoryMeta):
        return tree.constants
    if isinstance(tree, tuple):
        _, op, children = tree
        return list(map(lambda cs: op(*cs), product(*map(realize, children))))


def realize_trees(trees: list[AbsTree]) -> list[Category]:
    return [real for tree in trees for real in realize(tree)]


@dataclass
class Grammar:
    rules:  list[Rule]

    def generate(self, goal: CategoryMeta, depth: int, filter_empty: bool = True):
        ret = self.induction([goal], depth + 1)
        return list(filter(realizable, ret)) if filter_empty else ret

    def induction(self, options: list[AbsTree], depth: int) -> list[AbsTree]:
        return [] if depth == 0 else options + self.induction(self.expand_options(options), depth - 1)

    def expand_options(self, options: list[AbsTree]) -> list[AbsTree]:
        return [expand for option in options for expand in self.expand_tree(option)]

    def expand_tree(self, tree: AbsTree) -> list[AbsTree]:
        if isinstance(tree, CategoryMeta):
            return [(rule.lhs, rule.op, rule.rhs) for rule in self.applicable(tree)]
        top, op, children = tree
        branch_options = tuple(map(lambda branch: self.expand_tree(branch) + [branch], children))
        rs = [(top, op, prod) for prod in product(*branch_options)]
        return [r for r in rs if r != tree]

    def applicable(self, goal: CategoryMeta) -> list[Rule]:
        return [rule for rule in self.rules if rule.lhs == goal]
