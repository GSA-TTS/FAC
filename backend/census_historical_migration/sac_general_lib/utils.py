def create_json_from_db_object(gobj, mappings):
    json_obj = {}
    for mapping in mappings:
        if mapping.in_db is not None:
            value = getattr(gobj, mapping.in_db, mapping.default)
        else:
            value = mapping.default

        json_obj[mapping.in_form] = value
    return json_obj


def _boolean_field(json_obj, field_name):
    json_obj[field_name] = json_obj.get(field_name, "N") == "Y"
    return json_obj
