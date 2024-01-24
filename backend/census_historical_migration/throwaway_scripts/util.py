# Ceiling division
# We need to always round *up* so we don't miss any records.
import math


def cdiv(a, b):
    return math.ceil(a / b)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield list(map(str, lst[i : i + n]))


def trigger_migration_workflow(
    args, workflow_name="historic-data-migrator-with-pagination.yml"
):
    # The number of pages is the total records // instances
    recs_per_instance = cdiv(args.total_records, args.instances)
    print(f"Each instance must run {recs_per_instance} records.")
    page_size = cdiv(recs_per_instance, args.pages_per_instance)
    print(
        f"With {args.pages_per_instance} pages per instance, the page size is {page_size}."
    )
    total_pages = cdiv(args.total_records, page_size)
    print(f"There are {total_pages} pages in total.")
    print(f"This means we will attempt {total_pages * page_size} records.")
    # Run one extra page for good measure. This "rounds up."
    page_chunks = chunks(range(1, total_pages + 1), args.pages_per_instance)
    cmds = []
    for ndx, page_set in enumerate(page_chunks):
        # gh workflow run historic-data-migrator-with-pagination.yml -f environment=preview -f year=2022 -f page_size=1 -f pages=1
        cmds.append(
            [
                "gh",
                "workflow",
                "run",
                f"{workflow_name}",
                "-f",
                "environment=preview",
                "-f",
                f"year={args.year}",
                "-f",
                f"page_size={page_size}",
                "-f",
                "pages={}".format(",".join(page_set)),
            ]
        )
    return cmds
