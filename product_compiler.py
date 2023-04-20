
import numpy as np
import ijson
import sealed
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime
import itertools as itr
import yaml
from pathlib import Path

category_swap = {
	'': "",
	'subset': "sub",
	'commander_deck': "cmr",
	'draft_set': "dft",
	'prerelease_pack': 'pre',
	'bundle': "bndl",
	'booster_pack': "pack",
	'deck_box': "dbox",
	'booster_box': "bbox",
	'two_player_starter_set': "2plr",
	'case': "case",
	'land_station': "land",
	'box_set': "bset",
	'deck': "deck"
}

subtype_swap = {
	'': "",
	'secret_lair': "sld",
	'archenemy': "arch",
	'theme': "thm",
	'collector': "col",
	'draft': "dft",
	'deluxe': "del",
	'vip': "vip",
	'event': "evnt",
	'deck_builders_toolkit': "tkt",
	'battle_pack': "bpck",
	'minimal_packaging': "mpck",
	'intro': "intr",
	'clash': "clsh",
	'advanced': "adv",
	'from_the_vault': "ftv",
	'spellbook': "spb",
	'challenge': "chl",
	'planeswalker': "plw",
	'starter': "str",
	'planechase': "plnc",
	'set': "set",
	'jumpstart': "jmp",
	'topper': "tpr",
	'premium': "prem"
}

parentPath = Path("json/AllSetfiles/")
files = parentPath.glob("*.json")
t = tqdm(files)
products = []
codes = set()
for file in t:
	'''
	with open(file, 'rb') as ifile:
		booster_types = ijson.kvitems(ifile, "data.booster")
		types = list(dict(booster_types).keys())
		for t in types:
			print(file, "booster:", t)
	'''
	with open(file, 'rb') as ifile:
		sealed_product = list(ijson.items(ifile, "data.sealedProduct.item"))
		for p in sealed_product:
			codelist = [
				file.stem,
				category_swap[p.get("category", "")],
				subtype_swap[p.get("subtype", "")],
				"".join(filter(lambda c: c.isupper(), p["name"]))
			]
			code = "-".join(filter(None, codelist))
			code2 = code
			n = 1
			while code2 in codes:
				code2 = code + "-" + str(n)
				n += 1
			codes.add(code2)
			p.update({"contents":[], "code": code2})
			products.append(p)
t.close
del(t)

with open("products.yaml", 'w') as write:
	yaml.dump(products, write)
