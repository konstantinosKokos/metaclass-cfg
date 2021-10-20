from typing import Union, TypeVar, Iterator, Callable
from dataclasses import dataclass
from itertools import product, chain


class Category:
    surface:        tuple[str, ...]

    def __getitem__(self, item: int):
        return self.surface[item]


class CategoryMeta(type):
    arity:          int
    _constants:     list[Category] = []

    def __new__(mcs, name: str, arity: int = 1) -> type:
        def _init(cls, *surface: str) -> None:
            if len(surface) != arity:
                raise TypeError(f'Cannot initialize {mcs} of arity {arity} with an {len(surface)}-tuple.')
            cls.surface = surface

        def _repr(cls) -> str:
            return f'{name}(surface={str(cls.surface)})'

        def _hash(cls) -> int:
            return hash((type(cls), cls.surface))

        def _eq(cls, other: object) -> bool:
            return isinstance(other, Category) and hash(cls) == hash(other)

        return super().__new__(mcs, name, (Category,), {
            'arity': arity, '__init__': _init, '__repr__': _repr, '__hash__': _hash, '__eq__': _eq})

    def __init__(cls, _: str, arity: int = 1):
        super(CategoryMeta, cls).__init__(arity)

    def __hash__(cls) -> int:
        return hash((str(cls), cls.arity))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CategoryMeta) and hash(self) == hash(other)

    @property
    def constants(cls: 'CategoryMeta') -> list[Category]:
        return cls._constants

    @constants.setter
    def constants(cls, values: list[Union[str, tuple[str, ...]]]) -> None:
        cls._constants = list(map(cls, values)) if cls.arity == 1 else list(map(lambda val: cls(*val), values))

    def __str__(cls) -> str:
        return cls.__name__

    def __repr__(cls) -> str:
        return f"'{str(cls)}'"


@dataclass(unsafe_hash=True)
class AbsRule:
    lhs:            CategoryMeta
    rhs:            tuple[CategoryMeta, ...]
    multiplicity:   int

    def __init__(self, lhs: CategoryMeta, rhs: tuple[CategoryMeta, ...]):
        self.lhs = lhs
        self.rhs = rhs
        self.multiplicity = max(map(lambda cm: cm.arity, rhs))

    @classmethod
    def from_list(cls, signatures: list[tuple[CategoryMeta, tuple[CategoryMeta, ...]]]):
        return list(map(lambda s: cls(*s), signatures))


T = TypeVar('T')
Tree = Union[T, tuple[T, tuple['Tree', ...]]]
AbsTree = Tree[CategoryMeta]


def realizable(tree: AbsTree) -> bool:
    if isinstance(tree, CategoryMeta):
        return len(tree.constants) > 0
    if isinstance(tree, tuple):
        return all(map(realizable, tree[-1]))


@dataclass
class AbsGrammar:
    rules:          list[AbsRule]
    multiplicity:   int

    def __init__(self, rules: list[AbsRule]):
        self.rules = rules
        self.multiplicity = max(map(lambda rule: rule.multiplicity, rules))

    def generate(self, goal: CategoryMeta, depth: int, filter_empty: bool = True) -> Iterator[AbsTree]:
        # ret = self.expand_n([goal], depth)
        ret = self.expand_tree(goal, depth)
        ret = filter(realizable, ret) if filter_empty else ret
        ret = filter(lambda t: get_depth(t) == depth, ret)
        return ret

    # WE STILL NEED TO RETURN SINGLE CATEGORYMETAS....
    # BECAUSE WE MAY EXPAND SYMBOL A INTO B AND C, BUT B IS NOW DONE WHERE C STILL NEEDS TO BE EXPANDED. THEN THE
    # METHOD WILL STILL RETURN [] BECAUSE B CANNOT BE EXPANDED ANYMORE.
    # I THINK PRODUCT WILL RETURN [] IF ONE OF ITS OPERANDS DOES NOT HAVE ANY CONTENT OR SMTH.
    # def expand_one(self, tree: AbsTree) -> Iterator[AbsTree]:
    #     if isinstance(tree, CategoryMeta):
    #         if not self.applicable(tree):
    #             yield [[]]
    #         else:
    #             yield from ((tree, rule.rhs) for rule in self.applicable(tree))
    #     elif isinstance(tree, list):
    #         print(tree)
    #         yield [[]]
    #     else:
    #         root, children = tree
    #         yield from ((root, p) for p in product(*[list(self.expand_one(c)) for c in children]))
    #
    # def expand_n(self, fringe: Iterator[AbsTree], n: int) -> Iterator[AbsTree]:
    #     for i in range(n):
    #         fringe = chain.from_iterable(self.expand_one(tree) for tree in fringe)
    #     yield from fringe

    # def expand_tree(self, tree: AbsTree, depth: int) -> Iterator[tuple[int, AbsTree]]:
    #     if depth < 0:
    #         return
    #     if isinstance(tree, CategoryMeta):
    #         yield depth, tree
    #         for rule in self.applicable(tree):
    #             yield from self.expand_tree((tree, rule.rhs), depth - 1)
    #     else:
    #         root, children = tree
    #         options = product(*[list(self.expand_tree(c, depth)) for c in children])
    #         yield from ((d, (root, p)) for d, p in options)

    def expand_tree(self, tree: AbsTree, depth: int) -> Iterator[AbsTree]:
        if depth < 0:
            return
        if isinstance(tree, CategoryMeta):
            yield tree
            for rule in self.applicable(tree):
                yield from self.expand_tree((tree, rule.rhs), depth - 1)
        else:
            root, children = tree
            options = product(*[list(self.expand_tree(c, depth)) for c in children])
            yield from ((root, p) for p in options)

    def applicable(self, goal: CategoryMeta) -> list[AbsRule]:
        return [rule for rule in self.rules if rule.lhs == goal]


def map_tree(tree: Tree[CategoryMeta], f: Callable[[CategoryMeta], T]) -> Tree[T]:
    if isinstance(tree, CategoryMeta):
        return f(tree)
    head, children = tree
    return f(head), tuple(map(lambda c: map_tree(c, f), children))


def get_depth(tree: AbsTree) -> int:
    return 0 if isinstance(tree, CategoryMeta) else 1 + max([get_depth(c) for c in tree[1]])