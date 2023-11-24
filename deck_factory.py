# Deck factory

import sealed

def build_deck(config, prices, logger):
    booster = sealed.kit()
    price = 0
    if "mainBoard" in config:
        for location in ["mainBoard", "sideBoard", "commander"]:
            if location not in config:
                continue
            for card in config[location]:
                foiling = "foil" if card["isFoil"] else "normal"
                try:
                    price += prices[card["uuid"]][foiling] * card["count"]
                except:
                    logger.warning("Missing price for card {0}/{1}/{2}\n".format(card["setCode"], card["number"], foiling))
    elif "cards" in config:
        for card in config["cards"]:
            foiling = "normal" if card["finish"] == "nonfoil" else "foil"
            try:
                price += prices[card["uuid"]][foiling] * card["count"]
            except:
                logger.warning(f"Missing price for card {card['uuid']}\n")
    booster.add_card(price)
    return booster
