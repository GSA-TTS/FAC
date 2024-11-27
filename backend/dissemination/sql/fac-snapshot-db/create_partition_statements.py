import argparse
import sys

# for i in general federal_awards combined ; do python create_partition_statements.py general 20 ; done

# rm post/001_partitioning.sql ; for i in general federal_awards combined ; do python create_partition_statements.py $i >> post/001_partitioning.sql ; done


####################################
# by hash (makes no sense?)
####################################
def partition_by_sequence_hash():

    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument(
        "table_name", help="Table to create partition statements for", type=str
    )
    parser.add_argument("number_of_partitions", help="number of partitions", type=int)
    args = parser.parse_args()
    table_name = args.table_name
    number_of_partitions = args.number_of_partitions

    print(
        f"""
------------------------------------------------------
-- {table_name} - {number_of_partitions} partitions (hash seq)
------------------------------------------------------
"""
    )
    print("SET search_path TO public_data_v1_0_0;")

    print(
        f"ALTER TABLE public_data_v1_0_0.{table_name} RENAME TO {table_name}_to_be_removed;"
    )
    print(
        f"""CREATE TABLE public_data_v1_0_0.{table_name}
        (LIKE public_data_v1_0_0.{table_name}_to_be_removed)
        PARTITION BY hash(seq);
    """
    )

    for ndx in range(number_of_partitions):
        print(
            f"""
    DROP TABLE IF EXISTS public_data_v1_0_0.part_{table_name}_{ndx:02};
    CREATE TABLE public_data_v1_0_0.part_{table_name}_{ndx:02}
        PARTITION OF public_data_v1_0_0.{table_name}
        FOR VALUES WITH (modulus {number_of_partitions}, remainder {ndx});
    """
        )
    print(
        f"""
        INSERT INTO public_data_v1_0_0.{table_name}
        SELECT * FROM public_data_v1_0_0.{table_name}_to_be_removed;
        """
    )
    print(f"DROP TABLE public_data_v1_0_0.{table_name}_to_be_removed;")


####################################
# by audit year
####################################
def partition_by_audit_year():

    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument(
        "table_name", help="Table to create partition statements for", type=str
    )
    args = parser.parse_args()
    table_name = args.table_name

    print(
        f"""
------------------------------------------------------
-- {table_name} - partitions (audit_year)
------------------------------------------------------
-- python {' '.join(sys.argv)}
"""
    )
    print("SET search_path TO public_data_v1_0_0;")

    print(
        f"ALTER TABLE public_data_v1_0_0.{table_name} RENAME TO {table_name}_to_be_removed;"
    )
    print(
        f"""CREATE TABLE public_data_v1_0_0.{table_name}
        (LIKE public_data_v1_0_0.{table_name}_to_be_removed)
        PARTITION BY list(audit_year);
    """
    )

    for ndx in range(16, 30):
        print(
            f"""
    DROP TABLE IF EXISTS public_data_v1_0_0.part_{table_name}_20{ndx:02};
    CREATE TABLE public_data_v1_0_0.part_{table_name}_20{ndx:02}
        PARTITION OF public_data_v1_0_0.{table_name}
        FOR VALUES IN ('20{ndx:02}');
    """
        )
    print(
        f"""
    INSERT INTO public_data_v1_0_0.{table_name}
        SELECT * FROM public_data_v1_0_0.{table_name}_to_be_removed;
        """
    )
    print(f"DROP TABLE public_data_v1_0_0.{table_name}_to_be_removed;")


if __name__ == "__main__":
    # partition_by_sequence_hash()
    partition_by_audit_year()
