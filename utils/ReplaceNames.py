names = {
    'tanzania': 'united republic of tanzania',
    'comoros': 'comores',
}

def replace_names(country_name):
    country_name = country_name.strip().lower()
    for old_name, new_name in names.items():
        if old_name.find(country_name) != -1:
            return new_name

    return country_name

