
#Private:
def _invert_dict(in_dict):
    result = {}
    for key in in_dict.keys():
        value = in_dict[key]
        if isinstance(value, list):
            for inner_value in value:
                result[inner_value] = key
        else:
            result[value] = key
    return result

BUTTON_COFFEE_TEXT = "Coffee ☕"
BUTTON_BEER_TEXT = "Beer 🍺"
BUTTON_DINNER_TEXT = "Dinner 🍷"
BUTTON_DRINKS_TEXT = "Drinks 🥃"
BUTTON_PARK_TEXT = "Park 🌳"
BUTTON_SIGHT_TEXT = "Sight 🗽"
BUTTON_MUSEUM_TEXT = "Museum 🏛️"
BUTTON_CINEMA_TEXT = "Cinema 🍿"
BUTTON_ENTERTAINMENT_TEXT = "Entertainment 🕺"
VARIANT_BUTTONS = [BUTTON_COFFEE_TEXT, BUTTON_BEER_TEXT, BUTTON_DINNER_TEXT, BUTTON_DRINKS_TEXT,
                   BUTTON_PARK_TEXT, BUTTON_SIGHT_TEXT, BUTTON_MUSEUM_TEXT, BUTTON_CINEMA_TEXT, BUTTON_ENTERTAINMENT_TEXT]

QUERIES_TO_VARIATIONS = {'coffee': [BUTTON_COFFEE_TEXT, 'coffee', 'Coffee', '☕'],
                         'beer': [BUTTON_BEER_TEXT, 'beer', 'Beer', '🍺'],
                         'dinner': [BUTTON_DINNER_TEXT, 'dinner', 'Dinner', '🥗', 'food', 'Food'],
                         'bar': [BUTTON_DRINKS_TEXT, 'drinks', 'Drinks', 'bar', 'Bar', 'cocktail', 'Cocktail', 'cocktails', 'Cocktails'],
                         'park': [BUTTON_PARK_TEXT],
                         'sight': [BUTTON_SIGHT_TEXT],
                         'museum': [BUTTON_MUSEUM_TEXT],
                         'cinema': [BUTTON_CINEMA_TEXT],
                         'entertainment': [BUTTON_ENTERTAINMENT_TEXT]}
VARIATIONS_TO_QUERIES = _invert_dict(QUERIES_TO_VARIATIONS)

DISTANCE_BUTTONS = ['250', '500', '1000', '5000']

#Public:
def is_valid_variant(text):
    return text in VARIATIONS_TO_QUERIES

def variant_to_query(text):
    return VARIATIONS_TO_QUERIES.get(text, None)

def all_variant_buttons():
    return VARIANT_BUTTONS

def is_valid_distance(text):
    try:
        num = int(text)
        if num in range(50, 10000): return True
        else: return False
    except ValueError:
        return False

def all_distance_buttons():
    return DISTANCE_BUTTONS