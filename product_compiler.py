
import numpy as np
import ijson
import sealed
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime
import itertools as itr
from glob import glob

files = glob("json/AllSetfiles/*.json")
t = tqdm(files)
for file in t:
	with open(file, 'rb') as ifile:
		booster_types = ijson.kvitems(ifile, "data.booster")
		types = list(dict(booster_types).keys())
		for t in types:
			print(file, "booster:", t)
	with open(file, 'rb') as ifile:
		sealed_product = list(ijson.items(ifile, "data.sealedProduct.item"))
		for p in sealed_product:
			print(file, p["category"], p.get("subtype"), p["name"])
t.close
del(t)
