from django.core.exceptions import ValidationError

def start_and_end_rows_of_all_columns_are_same(ir):
    # Every column should have the same start and end rows
    for sheet in ir:
        starts = set()
        ends = set()
        for range in sheet["ranges"]:
            starts.add(range["start_cell"]["row"])
            ends.add(range["end_cell"]["row"])
        if ((len(starts) != 1) 
            or (len(ends) != 1)
            or starts != {"2"}
            ):
            raise ValidationError(
                (
                    sheet["name"],
                    "",
                    "Workbook modified",
                    {
                        "text": "The named ranges in this workbook have been modified. Please download a new workbook and copy your work into it",
                        "link": "Intake checks: no link defined",
                    },
                )
            )

