
import numpy as np
import ijson
import sealed
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime
import itertools as itr
import warnings

def build_sheet(cards, prices, psource="tcgplayer", foil=false):
	foiling = "foil" if foil else "normal"
	sheet = sealed.kit()
	for uuid, rate in cards:
        try:
            l = [kv for kv in prices['paper'][psource]['retail'][foiling].items()]
            l.sort(reverse=True)
            sheet.add_card(l[0][1], rate)
        except:
        	warnings.warn("Missing price for card {0}/{1}".format(uuid, foiling))
    sheet.normalize()
    return sheet


def build_variant(sheets, contents):
	variant = sealed.kit()
	for sheet_name, sheet_count in contents.items():
		for i in range(scount):
			variant.merge_kit(sheets[sheet_name])
	return variant

def build_booster(config, prices, psource="tcgplayer"):
	booster = sealed.kit()
	sheets = {}
	for name, data in config["sheets"].items():
		sheets[name] = build_sheet(data["cards"], prices, psource, data["foil"])
	for version in config["boosters"]:
		version_kit = build_variant(sheets, version["contents"])
		booster.add_set(version_kit, weight=version["weight"])
	booster.normalize()
	return booster
	