# Support - Cog/Over

## Overview

## Utility for testing cog/over 

check_cog_over_for_year is a command used for testing cog/over with a lot of Prod data.  The calculated cog/over value is compared with the value in the Prod data.  In Prod, a cog/over assignment can be overridden by customers.  Hence, the calculated cog/over value may not always match the value in the Prod data.  

The check_cog_over_for_year command keeps track of the number of matches / mismatches and prints the information.  No action is required for mismatches.

However, if a dataset with no overridden cog/over values is used, the check_cog_over_for_year command should not find any mismatches.

The allowed input value for year is 2022 / 2023 / 2024.


- check_cog_over_for_year.py - Test cog/over with 2022 or 2023 or data.  The default year is 2022.

```bash
docker compose run --rm web python manage.py check_cog_over_for_year --year 2022
```

```bash
docker compose run --rm web python manage.py check_cog_over_for_year --year 2023
```

```bash
docker compose run --rm web python manage.py check_cog_over_for_year --year 2024
```

