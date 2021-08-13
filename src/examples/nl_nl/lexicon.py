from src import cwdir
import os


_data_dir = os.path.join(cwdir, 'examples/nl_nl/data/')
_de_noun_path = os.path.join(_data_dir, 'de_personen.txt')
_het_noun_path = os.path.join(_data_dir, 'het_personen.txt')
_obj_cv_path = os.path.join(_data_dir, 'obj_control_verbs.txt')
_sub_cv_path = os.path.join(_data_dir, 'sub_control_verbs.txt')
_inf_path = os.path.join(_data_dir, 'infinitives.txt')


def _load_plain(path: str) -> list[str]:
    return [ln.strip() for ln in open(path, 'r').readlines()]


def _load_control_verbs(path: str) -> tuple[list[str], list[str]]:
    with open(path, 'r') as infile:
        verbs_present, verbs_inf = zip(*[ln.strip().split('\t') for ln in infile.readlines()])
    return list(verbs_present), list(verbs_inf)


_de_nouns = _load_plain(_de_noun_path)
_het_nouns = _load_plain(_het_noun_path)
_obj_control_verbs_present, _obj_control_verbs_inf = _load_control_verbs(_obj_cv_path)
_sub_control_verbs_present, _sub_control_verbs_inf = _load_control_verbs(_sub_cv_path)
_infinitive_verbs = _load_plain(_inf_path)


class Lexicon:
    @staticmethod
    def de_nouns():
        return list(iter(_de_nouns))

    @staticmethod
    def het_nouns():
        return list(iter(_het_nouns))

    @staticmethod
    def obj_control_verbs_present():
        return list(iter(_obj_control_verbs_present))

    @staticmethod
    def obj_control_verbs_inf():
        return list(iter(_obj_control_verbs_inf))

    @staticmethod
    def sub_control_verbs_present():
        return list(iter(_sub_control_verbs_present))

    @staticmethod
    def sub_control_verbs_inf():
        return list(iter(_sub_control_verbs_inf))

    @staticmethod
    def infinitive_verbs():
        return list(iter(_infinitive_verbs))