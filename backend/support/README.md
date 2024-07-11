# Support - Cog/Over

## Utility for testing cog/over 

The `check_cog_over_for_year` command compares calculated cog/over values against production data / test data loaded in LOCAL environment. In production data, users can override a cog/over assignment, resulting in a mismatch. 

The `check_cog_over_for_year` command keeps track of the number of matches / mismatches and prints the information. No action is required for mismatches if production data is used. If the test dataset does not include any overridden cog/over values, there will not be any mismatches.


## How to use `check_cog_over_for_year` command
Invoke the command like any other Django management command:
```bash
python manage.py check_cog_over_for_year --year 2024
```
The command accepts a single argument: `--year`, which can be one of `2022`, `2023`, or `2024`.

