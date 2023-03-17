# Sealed kit

import numpy as np
import pandas as pd
import ijson
from tqdm import tqdm

class kit:
    
    def __init__(self):
        self.distr = np.array([])
        
    def price_to_index(self, f):
        return np.round(np.log1p(f) * 100).astype(int)
        
    def index_to_price(self, i):
        return np.round(self.index_to_price_clean(i), 2)
    
    def index_to_price_clean(self, i):
        return np.expm1(i/100.0)
        
    def convolve(self, d1, d2):
        indexes = np.indices((len(d2), len(d1)))
        indexes = self.index_to_price_clean(indexes)
        indexes = np.sum(indexes, axis=0)
        indexes = self.price_to_index(indexes)
        maxlen = np.amax(indexes)+1
        mvalues = np.expand_dims(d1, 0) * np.expand_dims(d2, 1)
        temp = np.array(
            [np.sum(mvalues, where=indexes==i) for i in range(maxlen)]
        )
        return temp
    
    def add_card(self, price, weight = 1.0):
        if price is None:
            return False
        if weight == 0.0:
            return
        pid = self.price_to_index(price)
        if len(self.distr) > pid:
            self.distr[pid] += weight
        else:
            self.distr = np.append(self.distr,
                                   [0]*(pid-len(self.distr))+[weight],
                                   0)
        return True
    
    def add_series(self, pd_series, prices, foiling='normal'):
        for idx, uuid in pd_series.iteritems():
            self.add_card(prices[uuid][foiling])
    
    def add_set(self, new_kit, weight = 1, norm=False):
        if norm:
            weight /= np.sum(new_kit.distr)
        if len(self.distr) > len(new_kit.distr):
            self.distr[:len(new_kit.distr)] += new_kit.distr * weight
        else:
            c = new_kit.distr * weight
            c[:len(self.distr)] += self.distr
            self.distr = c
    
    def merge_kit(self, new_kit):
        if len(new_kit.distr) == 0:
            return
        if len(self.distr) == 0:
            self.distr = new_kit.distr
        else:
            self.distr = self.convolve(self.distr, new_kit.distr)
            
    def normalize(self):
        self.distr /= sum(self.distr)
    
    def summary(self):
        return [self.mean] + self.quartiles 
    
    @property
    def mean(self):
        if len(self.distr) == 0:
            return 0
        return np.round(np.sum(self.distr * np.array([self.index_to_price(x) for x in range(len(self.distr))]))/np.sum(self.distr), 2)
    
    @property
    def median(self):
        if len(self.distr) == 0:
            return 0
        u = np.cumsum(self.distr)
        if sum(self.distr) % 2 == 0:
            check = sum(self.distr)/2.0
            a = np.where(u > check)[0][0]
            b = np.where(u > check - 1)[0][0]
            return (self.index_to_price(a)+self.index_to_price(b))/2
        return self.index_to_price(np.where(u > sum(self.distr)/2.0)[0][0])
    
    @property
    def mode(self):
        if len(self.distr) == 0:
            return 0
        return self.index_to_price(np.argmax(self.distr))
        
    @property
    def max(self):
        if len(self.distr) == 0:
            return 0
        return self.index_to_price(len(self.distr)-1)
    
    @property
    def min(self):
        if len(self.distr) == 0:
            return 0
        return self.index_to_price(np.argwhere(self.distr).squeeze()[0])
    
    @property
    def quartiles(self):
        if len(self.distr) == 0:
            return [0, 0, 0, 0, 0]
        u = np.cumsum(self.distr)/sum(self.distr)
        q0 = self.index_to_price(np.where(u > 0.01)[0][0])
        q1 = self.index_to_price(np.where(u > 0.25)[0][0])
        q2 = self.index_to_price(np.where(u > 0.5)[0][0])
        q3 = self.index_to_price(np.where(u > 0.75)[0][0])
        q4 = self.index_to_price(np.where(u > 0.99)[0][0])
        return [q0, q1, q2, q3, q4]
    
    @property
    def prices(self):
        return [self.index_to_price(x) for x in range(len(self.distr))]

class card:
    def __init__(self, json_in):
        self.name = json_in["name"]
        self.prices = {}
        self.rarity = json_in["rarity"]
        self.styles = {}
    
    def add_style(self, json_in, style_name, unique=False):
        if unique:
            style_name += str(len(self.styles))
        self.styles.update({style_name: json_in["uuid"]})
        self.prices.update({style_name: {"foil": None, "normal": None}})
    
    def add_price(self, style, condition, price):
        if price is None:
            return False
        self.prices[style][condition] = price
        return True
    
    def add_prices(self, priceJson):
        ret = ""
        for s in self.styles.keys():
            ret += s
            if not self.add_price(s, 'foil', priceJson[self.styles[s]].get('foil')):
                ret += "noFoil"
            if not self.add_price(s, 'normal', priceJson[self.styles[s]].get('normal')):
                ret += "noNorm"
        if "no" in ret:
            return ret
    
    def print_prices(self):
        for style, sub in self.prices.items():
            print("{0}: ".format(style))
            for condition, price in sub.items():
                print("    {0}: {1}".format(condition, price))
            
def get_price_data(file):
    Json_Data = {}

    with open(file, "rb") as f:
        data = ijson.kvitems(f, 'data')
        dq = tqdm(data)
        dq.set_description("Loading price data")
        for card_id, prices in dq:
            #print(card_id)
            Temp = {}
            try:
                l = [kv for kv in prices['paper']['tcgplayer']['retail']['normal'].items()]
                l.sort(reverse=True)
                Temp['normal'] = float(l[0][1])
            except:
                try:
                    l = [kv for kv in prices['paper']['cardsphere']['retail']['normal'].items()]
                    l.sort(reverse=True)
                    Temp['normal'] = float(l[0][1])
                except:
                    try:
                        l = [kv for kv in prices['paper']['cardkingdom']['retail']['normal'].items()]
                        l.sort(reverse=True)
                        Temp['normal'] = float(l[0][1])
                    except:
                        pass
            try:
                l = [kv for kv in prices['paper']['tcgplayer']['retail']['foil'].items()]
                l.sort(reverse=True)
                Temp['foil'] = float(l[0][1])
            except:
                try:
                    l = [kv for kv in prices['paper']['cardsphere']['retail']['foil'].items()]
                    l.sort(reverse=True)
                    Temp['foil'] = float(l[0][1])
                except:
                    try:
                        l = [kv for kv in prices['paper']['cardkingdom']['retail']['foil'].items()]
                        l.sort(reverse=True)
                        Temp['foil'] = float(l[0][1])
                    except:
                        pass
            Json_Data[card_id] = Temp
        dq.close()
        del(dq)
    return Json_Data

def build_booster(Slots, contents, n_packs, label="", topper=None):
    booster = kit()
    cq = tqdm(contents)
    cq.set_description(" ".join(["Creating", label, "booster"]))
    for s in cq:
        booster.merge_kit(Slots[s])
    booster.normalize()
    cq.close()
    del(cq)
    
    box = kit()
    bq = tqdm(range(n_packs))
    bq.set_description(" ".join(["Creating", label, "box"]))
    for i in bq:
        box.merge_kit(booster)
    if isinstance(topper, kit):
        box.merge_kit(topper)
    bq.close()
    del(bq)
    box.normalize()
    
    return booster, box
                