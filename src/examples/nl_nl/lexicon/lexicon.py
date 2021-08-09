import os
from .config import data_folder

de_noun_fn = os.path.join(data_folder, 'processed/de_personen.txt')
het_noun_fn = os.path.join(data_folder, 'processed/het_personen.txt')
de_nouns = [ln.strip() for ln in open(de_noun_fn, 'r').readlines()]
het_nouns = [ln.strip() for ln in open(het_noun_fn, 'r').readlines()]

subj_control_verbs_present_tense = ['belooft', 'meldt', 'zegt', 'garandeert', 'vertelt', 'bezweert', 'antwoordt', 'verzekert', 'zweert']
subj_control_verbs_inf = ['beloven', 'melden', 'zeggen', 'garanderen', 'vertellen', 'bezweren', 'antwoorden',
                          'verzekeren', 'zweren']

obj_control_verbs_present_tense = ['smeekt', 'helpt', 'sommeert', 'instrueert', 'gebaart', 'ontraadt', 'traint', 'vraagt', 'overtuigt',
                                   'gunt', 'verwijt', 'motiveert', 'machtigt', 'dwingt', 'verplicht', 'commandeert', 'beweegt', 'beveelt',
                                   'prikkelt', 'verbiedt', 'verhindert', 'verleidt', 'belet', 'gelast', 'gebiedt', 'overreedt', 'stimuleert',
                                   'waarschuwt', 'leert', 'suggereert', 'verzoekt', 'adviseert', 'belemmert']
obj_control_verbs_inf = ['smeken', 'helpen', 'sommeren', 'instrueren', 'gebaren', 'ontraden', 'trainen', 'vragen',
                         'overtuigen', 'gunnen', 'verwijten', 'motiveren', 'machtigen',  'dwingen', 'verplichten',
                         'commanderen', 'bewegen', 'bevelen', 'prikkelen', 'overhalen', 'verbieden', 'verhinderen',
                         'verleiden', 'beletten', 'gelasten' 'gebieden', 'overreden', 'stimuleren', 'waarschuwen',
                         'leren', 'suggereren', 'verzoeken', 'adviseren', 'belemmeren']

infinitive_verbs = ['vertrekken', 'gaan', 'komen', 'winnen', 'verliezen', 'praten', 'stoppen', 'beginnen', 'kijken', 'stemmen']

