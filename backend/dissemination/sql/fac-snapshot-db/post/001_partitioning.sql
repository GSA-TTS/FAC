
------------------------------------------------------
-- general - partitions (audit_year)
------------------------------------------------------
-- python create_partition_statements.py general

SET search_path TO public_data_v1_0_0;
ALTER TABLE public_data_v1_0_0.general RENAME TO general_to_be_removed;
CREATE TABLE public_data_v1_0_0.general
        (LIKE public_data_v1_0_0.general_to_be_removed)
        PARTITION BY list(audit_year);
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2016;
    CREATE TABLE public_data_v1_0_0.part_general_2016
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2016');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2017;
    CREATE TABLE public_data_v1_0_0.part_general_2017
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2017');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2018;
    CREATE TABLE public_data_v1_0_0.part_general_2018
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2018');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2019;
    CREATE TABLE public_data_v1_0_0.part_general_2019
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2019');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2020;
    CREATE TABLE public_data_v1_0_0.part_general_2020
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2020');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2021;
    CREATE TABLE public_data_v1_0_0.part_general_2021
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2021');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2022;
    CREATE TABLE public_data_v1_0_0.part_general_2022
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2022');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2023;
    CREATE TABLE public_data_v1_0_0.part_general_2023
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2023');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2024;
    CREATE TABLE public_data_v1_0_0.part_general_2024
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2024');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2025;
    CREATE TABLE public_data_v1_0_0.part_general_2025
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2025');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2026;
    CREATE TABLE public_data_v1_0_0.part_general_2026
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2026');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2027;
    CREATE TABLE public_data_v1_0_0.part_general_2027
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2027');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2028;
    CREATE TABLE public_data_v1_0_0.part_general_2028
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2028');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_general_2029;
    CREATE TABLE public_data_v1_0_0.part_general_2029
        PARTITION OF public_data_v1_0_0.general 
        FOR VALUES IN ('2029');
    

    INSERT INTO public_data_v1_0_0.general
        SELECT * FROM public_data_v1_0_0.general_to_be_removed;
        
DROP TABLE public_data_v1_0_0.general_to_be_removed;

------------------------------------------------------
-- federal_awards - partitions (audit_year)
------------------------------------------------------
-- python create_partition_statements.py federal_awards

SET search_path TO public_data_v1_0_0;
ALTER TABLE public_data_v1_0_0.federal_awards RENAME TO federal_awards_to_be_removed;
CREATE TABLE public_data_v1_0_0.federal_awards
        (LIKE public_data_v1_0_0.federal_awards_to_be_removed)
        PARTITION BY list(audit_year);
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2016;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2016
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2016');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2017;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2017
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2017');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2018;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2018
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2018');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2019;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2019
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2019');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2020;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2020
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2020');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2021;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2021
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2021');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2022;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2022
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2022');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2023;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2023
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2023');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2024;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2024
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2024');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2025;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2025
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2025');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2026;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2026
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2026');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2027;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2027
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2027');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2028;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2028
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2028');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_federal_awards_2029;
    CREATE TABLE public_data_v1_0_0.part_federal_awards_2029
        PARTITION OF public_data_v1_0_0.federal_awards 
        FOR VALUES IN ('2029');
    

    INSERT INTO public_data_v1_0_0.federal_awards
        SELECT * FROM public_data_v1_0_0.federal_awards_to_be_removed;
        
DROP TABLE public_data_v1_0_0.federal_awards_to_be_removed;

------------------------------------------------------
-- combined - partitions (audit_year)
------------------------------------------------------
-- python create_partition_statements.py combined

SET search_path TO public_data_v1_0_0;
ALTER TABLE public_data_v1_0_0.combined RENAME TO combined_to_be_removed;
CREATE TABLE public_data_v1_0_0.combined
        (LIKE public_data_v1_0_0.combined_to_be_removed)
        PARTITION BY list(audit_year);
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2016;
    CREATE TABLE public_data_v1_0_0.part_combined_2016
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2016');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2017;
    CREATE TABLE public_data_v1_0_0.part_combined_2017
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2017');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2018;
    CREATE TABLE public_data_v1_0_0.part_combined_2018
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2018');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2019;
    CREATE TABLE public_data_v1_0_0.part_combined_2019
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2019');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2020;
    CREATE TABLE public_data_v1_0_0.part_combined_2020
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2020');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2021;
    CREATE TABLE public_data_v1_0_0.part_combined_2021
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2021');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2022;
    CREATE TABLE public_data_v1_0_0.part_combined_2022
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2022');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2023;
    CREATE TABLE public_data_v1_0_0.part_combined_2023
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2023');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2024;
    CREATE TABLE public_data_v1_0_0.part_combined_2024
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2024');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2025;
    CREATE TABLE public_data_v1_0_0.part_combined_2025
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2025');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2026;
    CREATE TABLE public_data_v1_0_0.part_combined_2026
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2026');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2027;
    CREATE TABLE public_data_v1_0_0.part_combined_2027
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2027');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2028;
    CREATE TABLE public_data_v1_0_0.part_combined_2028
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2028');
    

    DROP TABLE IF EXISTS public_data_v1_0_0.part_combined_2029;
    CREATE TABLE public_data_v1_0_0.part_combined_2029
        PARTITION OF public_data_v1_0_0.combined 
        FOR VALUES IN ('2029');
    

    INSERT INTO public_data_v1_0_0.combined
        SELECT * FROM public_data_v1_0_0.combined_to_be_removed;
        
DROP TABLE public_data_v1_0_0.combined_to_be_removed;
