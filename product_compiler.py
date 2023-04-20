
import numpy as np
import ijson
import sealed
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime
import itertools as itr
from glob import glob
import yaml

files = glob("json/AllSetfiles/*.json")
t = tqdm(files)
products = []
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
			p.update({"contents":[]})
			products.append(p)
t.close
del(t)

with open("products.yaml", 'w') as write:
	yaml.dump(products, write)
