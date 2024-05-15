# Support - Cog/Over

## Overview

## Utility for testing cog/over 

run_2022_23 is a command used for testing cog/over with a lot of Prod data.  The calculated cog/over is compared with the value in the Prod data.  In Prod, a cog/over assignment can be overridden by customers.  Hence, the calculated cog/over value may not always match the value in the Prod data.  

The run_2022_23 command keeps track of the number of matches / mismatches and prints the information.  No action is required for mismatches.

However, if a dataset with no overridden cog/over values is used, the run_2022_23 command should not find any mismatches.


- run_2022_23.py - Test cog/over with 2022 or 2023 data.  The default year is 2022.

```bash
docker compose run --rm web python manage.py run_2022_23 --year 2022
```

```bash
docker compose run --rm web python manage.py run_2022_23 --year 2023
```

