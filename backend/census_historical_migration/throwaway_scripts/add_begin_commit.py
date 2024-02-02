import argparse

# To use this script, run `python add_begin_commit.py input.sql -o output.sql`
# or `python add_begin_commit.py input.sql` to use the default output file name
# The input file will be read and the output file will be written
# Example: python census_historical_migration/throwaway_scripts/add_begin_commit.py dissemination_general.sql

parser = argparse.ArgumentParser(
    description="Surround INSERT statements with BEGIN and COMMIT in a SQL file."
)
parser.add_argument("input_file", type=str, help="Path to the input SQL file")
parser.add_argument(
    "-o",
    "--output_file",
    type=str,
    help="Path to the output SQL file",
    default="output.sql",
    required=False,
)
args = parser.parse_args()


def process_sql_file(input_file_path, output_file_path):
    # Open the input SQL file for reading
    print(f"Processing {input_file_path} and writing to {output_file_path}")
    with open(input_file_path, "r") as input_file:
        # Open the output SQL file for writing
        with open(output_file_path, "w") as output_file:
            # Keep track of whether we're inside an INSERT statement
            inside_insert = False

            for line in input_file:
                # Check if the line is the start of an INSERT statement
                if line.strip().upper().startswith("INSERT"):
                    output_file.write("BEGIN;\n")
                    inside_insert = True

                output_file.write(line)

                # If we're inside an INSERT statement and the line ends with a semicolon, write "COMMIT;"
                if inside_insert and line.strip().endswith(";"):
                    output_file.write("COMMIT;\n")
                    inside_insert = False
    print("Done!")


if __name__ == "__main__":
    # Parse the command line arguments
    args = parser.parse_args()

    # Call the function to process the file
    process_sql_file(args.input_file, args.output_file)
