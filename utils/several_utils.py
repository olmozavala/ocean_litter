"""Small helpers shared by simulation filenames and country-statistics readers."""

from __future__ import annotations

from datetime import datetime


names = {
    'tanzania': 'united republic of tanzania',
    'comoros': 'comores',
}

def replace_names(country_name: str) -> str:
    """Normalize a country label to lowercase and apply historical aliases.

    The existing alias lookup accepts substrings of alias keys; it is not an
    exact-name lookup. Keep input country labels complete to avoid collisions.
    """
    country_name = country_name.strip().lower()
    for old_name, new_name in names.items():
        if old_name.find(country_name) != -1:
            return new_name

    return country_name


def str2bool(v: str) -> bool:
    """Parse CLI flags: yes, true, t, and 1 are true, ignoring case.

    All other strings are false; whitespace is not stripped.
    """
    return v.lower() in ("yes", "true", "t", "1", "True")


def get_file_name(name: str, start_date: datetime, end_date: datetime, part_n: int) -> str:
    """Return ``NAME_YYYY-MM-DD_YYYY-MM-DD`` without a file extension.

    Hours are discarded. ``part_n`` is retained for existing callers but does
    not appear in the filename; callers must avoid same-day name collisions.
    """
    time_format_red = "%Y-%m-%d"
    # return F"{name}_{start_date.strftime(time_format_red)}_{end_date.strftime(time_format_red)}__{part_n:02d}"
    return F"{name}_{start_date.strftime(time_format_red)}_{end_date.strftime(time_format_red)}"

