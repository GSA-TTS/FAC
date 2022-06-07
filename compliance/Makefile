generate:
	trestle author ssp-generate -p lato -o dist/system-security-plans/lato -y status_header.yaml -phv

assemble:
	trestle author ssp-assemble --markdown dist/system-security-plans/ --output lato

status:
	grep -R "\- c\-" dist/system-security-plans/* | cut -d':' -f2 | sort | uniq -c

# pull down the NIST catalogs directly for examination
reference:
	trestle import -f https://github.com/usnistgov/oscal-content/raw/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_LOW-baseline-resolved-profile_catalog.json -o nist-sp-800-53-rev5-low
	trestle import -f https://github.com/usnistgov/oscal-content/raw/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_MODERATE-baseline-resolved-profile_catalog.json -o nist-sp-800-53-rev5-moderate
	trestle import -f https://github.com/usnistgov/oscal-content/raw/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_HIGH-baseline-resolved-profile_catalog.json -o nist-sp-800-53-rev5-high
