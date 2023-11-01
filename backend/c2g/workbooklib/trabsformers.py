from c2g.models import ELECAUDITHEADER as Gen, ELECAUDITS as Cfda


def get_cpacpuntry(country: str):
    if country.upper() in ["", "US", "USA"]:
        cpacountry = "USA"
    else:
        cpacountry = "non-USA"
    return cpacountry


def normalize_entity_type(entity_type: str):
    entity_type = entity_type.lower()
    if entity_type == "local government":
        entity_type = "local"
    return entity_type


def normalize_zip(zip):
    strzip = str(zip)
    if len(strzip) == 9:
        return f"{strzip[0:5]}-{strzip[5:9]}"
    return strzip


def clean_gen(gen: Gen):
    gen.ENTITY_TYPE = normalize_entity_type(gen.ENTITY_TYPE)
    gen.CPACOUNTRY = get_cpacpuntry(gen.CPACOUNTRY)
    gen.UEI = gen.UEI or "BADBADBADBAD"


def clean_cfda(cCda: Cfda):
    "Placeholder for cfda cleanup code"
    pass
