import pandas as pd

def case1():
    country_list_asia = ('Bahrain', 1, 4,  # Not shown
                         'Bangladesh', 5, 787,
                         'Myanmar', 792, 458,
                         'Cambodia', 1250, 30,
                         'China', 1280, 8820,
                         'India', 10100, 600,
                         'Indonesia', 10700, 3300,
                         'Iran', 14000, 247,
                         'Japan', 14247, 143,
                         'South Korea', 14390, 34,
                         'Kuwait', 14424, 11,
                         'Malaysia', 14435, 937,
                         'Oman', 15372, 5,
                         'Pakistan', 15377, 480,
                         'Philippines', 15857, 1884,
                         'Saudi Arabia', 17741, 21,
                         'Singapore', 17762, 6,  # Not shown
                         'Sri lanka', 17768, 1591,
                         'Thailand', 19359, 1028,
                         'United Arab Emirates', 20387, 3,
                         'Vietnam', 20390, 1834,
                         'Yemen', 22224, 169)
    country_list_africa = ('algeria', 1, 521,
                           'angola', 522, 63,
                           'benin', 585, 43,
                           'cameroon', 628, 28,
                           'cabo verde', 656, 9,
                           'comores', 665, 58,
                           'democratic republic of the congo', 723, 15,
                           'republic of the congo', 738, 17,
                           "Ivory Coast", 755, 195,
                           'djibouti', 950, 17,
                           'egypt', 967, 967,
                           'eritrea', 1934, 16,
                           'gabon', 1950, 6,
                           'gambia', 1956, 20,
                           'ghana', 1976, 92,
                           'guinea bissau', 2068, 20,
                           'equatorial guinea', 2088, 6,
                           'guinea', 2094, 19,
                           'kenya', 2113, 23,
                           'liberia', 2136, 57,
                           'libya', 2193, 53,
                           'madagascar', 2246, 35,
                           'mauritania', 2281, 14,
                           'mauritius', 2295, 56,  # * Not shown
                           'morocco', 2351, 310,
                           'mozambique', 2661, 46,
                           'namibia', 2707, 5,
                           'nigeria', 2712, 851,
                           'sao tome and principe', 3563, 5,  # * Not shown
                           'senegal', 3568, 255,
                           'seychelles', 3823, 5,  # * Victoria
                           'sierra leone', 3828, 36,
                           'somalia', 3864, 102,
                           'south africa', 3966, 630,
                           'sudan', 4596, 23,
                           'united republic of tanzania', 4619, 49,
                           'togo', 4668, 35,
                           'tunisia', 4703, 234)
    return country_list_asia, country_list_africa


