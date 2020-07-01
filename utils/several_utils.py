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


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1", "True")


def get_file_name(name, start_date, end_date, part_n):
    time_format_red = "%Y-%m-%d"
    # return F"{name}_{start_date.strftime(time_format_red)}_{end_date.strftime(time_format_red)}__{part_n:02d}"
    return F"{name}_{start_date.strftime(time_format_red)}_{end_date.strftime(time_format_red)}"

