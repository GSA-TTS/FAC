"""
Custom tag to combine continuous years into hyphen-separated ranges
Example: ["2018", "2019", "2020", "2024"] to "2018-2020, 2024"
"""

from django import template

register = template.Library()


@register.filter()
def combine_years(value):
    if not value:
        return ""
    years = sorted(int(year) for year in value)  # Baseline, cast to int and sort

    # For each year, either count right one or append the established value.
    ranges = []
    start = prev = years[0]
    for year in years[1:]:
        if year == prev + 1:
            prev = year
        else:
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            start = prev = year
    # Only one year
    if start == prev:
        ranges.append(str(start))
    # All values are continuous
    else:
        ranges.append(f"{start}-{prev}")

    return ", ".join(ranges)
