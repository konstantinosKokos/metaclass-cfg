# Random selection of nouns
import random
from mcfg.nouns import all_nouns
from mcfg.mcfg import Category, CategoryMeta

random.shuffle(all_nouns)
noun_gen = (n for n in all_nouns)


def get_nouns(idx):
    return [next(noun_gen) for _ in range(idx)]


def simple_concat(goal: CategoryMeta) -> Category:
    def compile_args(*args: Category):
        return goal(' '.join(map(lambda a: a[0], args)))
    return compile_args


def simple_flatten(*args: list[int]) -> list[int]:
    return (sum(map(lambda a: a[0], args), []),)
