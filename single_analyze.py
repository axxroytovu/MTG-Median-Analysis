import json
import requests
import sealed
import booster_factory as b_f
import matplotlib.pyplot as plt
import numpy as np

def chart_sheet(sheet, prices, threshold=False):
    data = []
    for card in sheet['cards']:
        foiling = 'foil' if card.get('foil', False) else 'normal'
        try:
            data.append((prices[card['uuid']][foiling], f"{card['set']}:{card['number']}", np.round(card['weight']/sheet['total_weight']*100, 2)))
        except KeyError:
            print(f"Data missing for {card['set']}:{card['number']}:{foiling}")
    data.sort(reverse=True)
    if threshold:
        for d in data:
            if d[0] < threshold:
                break
            print(d)
    else:
        for i in range(10):
            print(data[i])

def main():
    sealed_url = "https://raw.githubusercontent.com/taw/magic-sealed-data/master/sealed_extended_data.json"
    booster_req = requests.get(sealed_url)
    booster_data = json.loads(booster_req.content)
    
    analyze_code = 'lci-set'
    
    prices_url = "https://mtgjson.com/api/v5/AllPricesToday.json"
    prices_req = requests.get(prices_url)
    
    prices_data = json.loads(prices_req.content)["data"]
    prices_flatten = {}
    for uuid, prices in prices_data.items():
        prices_flatten[uuid] = {}
        try:
            prices_flatten[uuid]['normal'] = list(prices['paper']['cardmarket']['retail']['normal'].values())[0]
        except (KeyError, IndexError):
            pass
        try:
            prices_flatten[uuid]['foil'] = list(prices['paper']['cardmarket']['retail']['foil'].values())[0]
        except (KeyError, IndexError):
            pass
    
    for booster in booster_data:
        if booster['code'] != analyze_code:
            continue
        sheet_refactor = {}
        for sheet, contents in booster["sheets"].items():
            temp = {}
            temp['foil'] = contents['cards'][0].get("foil", False)
            temp['cards'] = {c["uuid"]:c["weight"] for c in contents['cards']}
            sheet_refactor[sheet] = temp
            print(sheet)
            chart_sheet(contents, prices_flatten, threshold = 1)
        booster_refactor = booster
        booster_refactor["sheets"] = sheet_refactor
        all_sheets, booster_vals = b_f.build_booster(booster_refactor, prices_flatten, verbose=True, bulkThreshold=0.5)
        for name, s in all_sheets.items():
            s.normalize()
            plt.figure()
            plt.plot(s.prices, s.distr * 100, label="Probability")
            plt.title(name)
            plt.xlabel("Cardmarket retail price [Euro]")
            plt.ylabel("Chance to pull [%]")
            plt.xscale("asinh")
            plt.yscale("asinh")
            print(name, s.mean, s.median)
            plt.axvline(s.mean, color='k', label='EV')
            plt.axvline(s.median, color='g', label='Median')
            plt.gca().set_xlim(left=0)
            plt.legend()
            plt.grid()
        
        plt.figure()
        booster_vals.normalize()
        plt.plot(booster_vals.prices, booster_vals.distr * 100, label="Probability")
        plt.title(booster["name"])
        plt.xlabel("Total Cardmarket retail value [Euro]")
        plt.ylabel("Chance to pull [%]")
        plt.xscale("asinh")
        plt.yscale("asinh")
        plt.gca().set_xlim(left=0)
        print("booster", booster_vals.mean, booster_vals.median)
        print(booster_vals.summary())
        plt.axvline(booster_vals.mean, color='k', label='EV')
        plt.axvline(booster_vals.median, color='g', label='Median')
        plt.grid()
        plt.legend()
        
        box = sealed.kit()
        for i in range(30):
            box.merge_kit(booster_vals)
        box.normalize()
        plt.figure()
        plt.plot(box.prices, box.distr * 100, label="Probability")
        plt.title(booster["name"] + " Box")
        plt.xlabel("Total Cardmarket retail value [Euro]")
        plt.ylabel("Chance to pull [%]")
        plt.xscale("asinh")
        plt.yscale("asinh")
        #plt.gca().set_xlim(left=0)
        print("booster", box.mean, box.median)
        print(box.summary())
        plt.axvline(box.mean, color='k', label='EV')
        plt.axvline(box.median, color='g', label='Median')
        plt.grid()
        plt.legend()
        
        plt.show()
    

if __name__ == "__main__":
    main()
