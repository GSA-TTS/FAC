Character limits are used here, in generating the schemas for validation, and in the greater application for web form fields and the like. 

Character limits were determined by pulling a large amount of data from a table and making a decision based on the stats.

1. Field length averages, medians, and min/max values were determined for string and int values.
    * Floats, or other value types, are initially set to zero.
2. Mins and maxes are separated into JSON to be included in this folder.
3. Character limits are determined based on the mins/maxes.
4. With outlier values, we use the average & median to make a decision.
    * Ex. The maximum length of 31439 in notes_to_sefa.accounting_policies, when the average & median are about 500.

Most fields will be unused initially.
