import json
from pprint import pprint


def get_vcap():
    # return json.loads(os.getenv("VCAP_SERVICES"))
    obj = json.load(open("example_vcap.json"))
    return obj


# eg "user-provided", "name", ""https-proxy-creds""
def from_array(arr, key, value):
    for o in arr:
        if o[key] == value:
            return o
    raise ValueError("Nope")


def at_path(vcap, keys):
    if isinstance(keys, str):
        keys = [keys]
    struct = vcap
    for k in keys:
        struct = struct[k]
    return struct


def vcap_lookup(key):
    vcap = get_vcap()


def setup_cgov_env():
    env = {}
    env["SSL_CERT_FILE"] = "/etc/ssl/certs/ca-certificates.crt"
    env["REQUESTS_CA_BUNDLE"] = "/etc/ssl/certs/ca-certificates.crt"
    env["https_proxy"] = at_path(
        from_array(at_path(get_vcap(), ["user-provided"]), "name", "https-proxy-creds"),
        ["credentials", "uri"],
    )
    env["smtp_proxy_domain"] = at_path(
        from_array(at_path(get_vcap(), ["user-provided"]), "name", "smtp-proxy-creds"),
        ["credentials", "domain"],
    )
    env["smtp_proxy_port"] = at_path(
        from_array(at_path(get_vcap(), ["user-provided"]), "name", "smtp-proxy-creds"),
        ["credentials", "port"],
    )

    #     S3_ENDPOINT_FOR_NO_PROXY="$(echo $VCAP_SERVICES | jq --raw-output --arg service_name "fac-public-s3" ".[][] | select(.name == \$service_name) | .credentials.endpoint")"
    #     S3_FIPS_ENDPOINT_FOR_NO_PROXY="$(echo $VCAP_SERVICES | jq --raw-output --arg service_name "fac-public-s3" ".[][] | select(.name == \$service_name) | .credentials.fips_endpoint")"
    #     S3_PRIVATE_ENDPOINT_FOR_NO_PROXY="$(echo $VCAP_SERVICES | jq --raw-output --arg service_name "fac-private-s3" ".[][] | select(.name == \$service_name) | .credentials.endpoint")"
    #     S3_PRIVATE_FIPS_ENDPOINT_FOR_NO_PROXY="$(echo $VCAP_SERVICES | jq --raw-output --arg service_name "fac-private-s3" ".[][] | select(.name == \$service_name) | .credentials.fips_endpoint")"
    #     export no_proxy="${S3_ENDPOINT_FOR_NO_PROXY},${S3_FIPS_ENDPOINT_FOR_NO_PROXY},${S3_PRIVATE_ENDPOINT_FOR_NO_PROXY},${S3_PRIVATE_FIPS_ENDPOINT_FOR_NO_PROXY},apps.internal"

    S3_ENDPOINT_FOR_NO_PROXY = at_path(
        from_array(at_path(get_vcap(), ["s3"]), "name", "fac-public-s3"),
        ["credentials", "endpoint"],
    )
    S3_FIPS_ENDPOINT_FOR_NO_PROXY = at_path(
        from_array(at_path(get_vcap(), ["s3"]), "name", "fac-public-s3"),
        ["credentials", "fips_endpoint"],
    )
    S3_PRIVATE_ENDPOINT_FOR_NO_PROXY = at_path(
        from_array(at_path(get_vcap(), ["s3"]), "name", "fac-private-s3"),
        ["credentials", "endpoint"],
    )
    S3_PRIVATE_FIPS_ENDPOINT_FOR_NO_PROXY = at_path(
        from_array(at_path(get_vcap(), ["s3"]), "name", "fac-private-s3"),
        ["credentials", "fips_endpoint"],
    )
    env["no_proxy"] = (
        f"{S3_ENDPOINT_FOR_NO_PROXY},{S3_FIPS_ENDPOINT_FOR_NO_PROXY},{S3_PRIVATE_ENDPOINT_FOR_NO_PROXY},{S3_PRIVATE_FIPS_ENDPOINT_FOR_NO_PROXY},apps.internal"
    )

    pprint(env)


if __name__ == "__main__":
    setup_cgov_env()
