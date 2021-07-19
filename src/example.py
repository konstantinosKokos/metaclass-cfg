from cfg import CategoryMeta, Grammar

# Define categories
N_sg_n, N_sg_g, N_pl = CategoryMeta.from_list(['N_sg_n', 'N_sg_g', 'N_pl'])

Det_sg_n, Det_sg_g, Det_pl, Adj = CategoryMeta.from_list(['Det_sg_n', 'Det_sg_g', 'Det_pl', 'Adj'])

NP_sg_1_nom, NP_sg_2_nom, NP_sg_3_nom, NP_pl_1_nom, NP_pl_2_nom, NP_pl_3_nom, NP_accu = CategoryMeta.from_list([
    'NP_sg_1_nom', 'NP_sg_2_nom', 'NP_sg_3_nom', 'NP_pl_1_nom', 'NP_pl_2_nom', 'NP_pl_3_nom', 'NP_accu'])

VP_sg_1, VP_sg_2, VP_sg_3, VP_pl_1, VP_pl_2, VP_pl_3 = CategoryMeta.from_list([
    'VP_sg_1', 'VP_sg_2', 'VP_sg_3', 'VP_pl_1', 'VP_pl_2', 'VP_pl_3'])

TE, INF, S, TI = CategoryMeta.from_list(['TE', 'INF', 'S', 'TI'])

# Define constants
N_sg_n.constants = ['dier', 'bier', 'kind']
N_sg_g.constants = ['man', 'vrouw']
N_pl.constants = ['mensen', 'vrouwen', 'dieren']
Det_sg_n.constants = ['het', 'een', 'geen', 'dit', 'dat']
Det_sg_g.constants = ['de', 'een', 'geen', 'die', 'deze']
Det_pl.constants = ['de', 'twee', 'drie', 'sommige', 'de beide']
NP_sg_1_nom.constants = ['ik']
NP_sg_2_nom.constants = ['je']
NP_sg_3_nom.constants = ['hij']
Adj.constants = ['witte', 'rode', 'zwarte']
TE.constants = ['te']
VP_sg_1.constants = ['beloof']
VP_sg_2.constants = ['belooft']
VP_sg_3.constants = ['belooft']
VP_pl_1.constants = ['beloven']
VP_pl_2.constants = ['beloven']
VP_pl_3.constants = ['beloven']
INF.constants = ['verlaten']
NP_accu.constants = ['hem', 'haar', 'je', 'ze', 'ons']


# Define rules
rules = [
    (NP_sg_3_nom,       [(Det_sg_n, N_sg_n), (Det_sg_g, N_sg_g), (Det_sg_n, Adj, N_sg_n), (Det_sg_g, Adj, N_sg_g)]),
    (NP_pl_3_nom,       [(N_pl,), (Det_pl, N_pl), (Det_pl, Adj, N_pl)]),
    (NP_accu,           [(Det_sg_n, N_sg_n), (Det_sg_g, N_sg_g), (Det_sg_n, Adj, N_sg_n), (Det_sg_g, Adj, N_sg_g),
                         (N_pl,), (Det_pl, N_pl), (Det_pl, Adj, N_pl)]),
    (TI,                [(TE, INF), (NP_accu, TE, INF)]),
    (S,                 [(NP_sg_1_nom, VP_sg_1, TI), (NP_sg_2_nom, VP_sg_2, TI), (NP_sg_3_nom, VP_sg_3, TI),
                         (NP_pl_1_nom, VP_pl_1, TI), (NP_pl_2_nom, VP_pl_2, TI), (NP_pl_3_nom, VP_pl_3, TI)])
]

# Define grammar
grammar = Grammar(rules)

# Generate sample phrases of type S with maximal tree depth 2
gens = list(grammar.realize(grammar.generate(S, 2)))

