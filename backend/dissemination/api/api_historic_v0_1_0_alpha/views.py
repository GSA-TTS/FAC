schema = "api_historic_v0_1_0_alpha"
prefix = "census_"

tables = {
    "agency": (16, 22),
    "captext": (19, 22),
    "captext_formatted": (19, 22),
    "cfda": (16, 22),
    "cpas": (16, 22),
    "duns": (16, 22),
    "eins": (16, 22),
    "findings": (16, 22),
    "findingstext": (19, 22),
    "findingstext_formatted": (19, 22),
    "gen": (16, 22),
    "notes": (19, 22),
    "passthrough": (16, 22),
    "revisions": (19, 22),
    "ueis": (22, 22),
}


def just_table_names(lot):
    return list(tables.keys())


def generate_views(tbs):
    print("begin;\n")
    for t, rng in tbs.items():
        # Range is exclusive on the second value
        for v in range(rng[0], rng[1] + 1):
            print(f"create view {schema}.{t}{v} as")
            print("\tselect *")
            print(f"\tfrom {prefix}{t}{v}")
            print(f"\torder by {prefix}{t}{v}.id")
            print(";\n")
    print("commit;")
    print("notify pgrst, 'reload schema';")


if __name__ in "__main__":
    generate_views(tables)

# (define (generate-drops lot)
#   (printf "begin;~n~n")
#   (for ([t lot])
#     (printf "drop table if exists ~a.~a;~n" schema t))
#   (printf "commit;~n")
#   (printf "notify pgrst, 'reload schema';~n"))
