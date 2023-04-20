# Deck factory

import sealed

def build_deck(config, prices):
	booster = sealed.kit()
	price = 0
	for location in ["cards", "sideboard", "commander"]:
		for card in config[location]:
			foiling = "foil" if card["foil"] else "normal"
			try:
				price += prices[card["mtgjson_uuid"]][foiling] * card["count"]
			except:
				with open("log.log", 'a') as file:
					file.write("Missing price for card {0}/{1}/{2}\n".format(card["set_code"], card["number"], foiling))
	booster.add_card(price)
	return booster
