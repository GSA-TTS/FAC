
-- but the tables are still in prod. This will remove them
-- from the prod environment, where they are no longer needed.
-- OLD RAW CENSUS DATA
-- our own data for this. We have removed this from the deploy,
-- Specifically, it was used in cog/over. However, we now use 
-- This data was an early part of the data migration. 
-- The cascade will get rid of any associated artifacts, which
-- we certainly do not want.
--------------------------------------
--------------------------------------
DROP TABLE IF EXISTS census_agency16 CASCADE;
DROP TABLE IF EXISTS census_agency17 CASCADE;
DROP TABLE IF EXISTS census_agency18 CASCADE;
DROP TABLE IF EXISTS census_agency19 CASCADE;
DROP TABLE IF EXISTS census_agency20 CASCADE;
DROP TABLE IF EXISTS census_agency21 CASCADE;
DROP TABLE IF EXISTS census_agency22 CASCADE;
DROP TABLE IF EXISTS census_captext_formatted19 CASCADE;
DROP TABLE IF EXISTS census_captext_formatted20 CASCADE;
DROP TABLE IF EXISTS census_captext_formatted21 CASCADE;
DROP TABLE IF EXISTS census_captext_formatted22 CASCADE;
DROP TABLE IF EXISTS census_captext19 CASCADE;
DROP TABLE IF EXISTS census_captext20 CASCADE;
DROP TABLE IF EXISTS census_captext21 CASCADE;
DROP TABLE IF EXISTS census_captext22 CASCADE;
DROP TABLE IF EXISTS census_cfda16 CASCADE;
DROP TABLE IF EXISTS census_cfda17 CASCADE;
DROP TABLE IF EXISTS census_cfda18 CASCADE;
DROP TABLE IF EXISTS census_cfda19 CASCADE;
DROP TABLE IF EXISTS census_cfda20 CASCADE;
DROP TABLE IF EXISTS census_cfda21 CASCADE;
DROP TABLE IF EXISTS census_cfda22 CASCADE;
DROP TABLE IF EXISTS census_cpas16 CASCADE;
DROP TABLE IF EXISTS census_cpas17 CASCADE;
DROP TABLE IF EXISTS census_cpas18 CASCADE;
DROP TABLE IF EXISTS census_cpas19 CASCADE;
DROP TABLE IF EXISTS census_cpas20 CASCADE;
DROP TABLE IF EXISTS census_cpas21 CASCADE;
DROP TABLE IF EXISTS census_cpas22 CASCADE;
DROP TABLE IF EXISTS census_duns16 CASCADE;
DROP TABLE IF EXISTS census_duns17 CASCADE;
DROP TABLE IF EXISTS census_duns18 CASCADE;
DROP TABLE IF EXISTS census_duns19 CASCADE;
DROP TABLE IF EXISTS census_duns20 CASCADE;
DROP TABLE IF EXISTS census_duns21 CASCADE;
DROP TABLE IF EXISTS census_duns22 CASCADE;
DROP TABLE IF EXISTS census_eins16 CASCADE;
DROP TABLE IF EXISTS census_eins17 CASCADE;
DROP TABLE IF EXISTS census_eins18 CASCADE;
DROP TABLE IF EXISTS census_eins19 CASCADE;
DROP TABLE IF EXISTS census_eins20 CASCADE;
DROP TABLE IF EXISTS census_eins21 CASCADE;
DROP TABLE IF EXISTS census_eins22 CASCADE;
DROP TABLE IF EXISTS census_findings16 CASCADE;
DROP TABLE IF EXISTS census_findings17 CASCADE;
DROP TABLE IF EXISTS census_findings18 CASCADE;
DROP TABLE IF EXISTS census_findings19 CASCADE;
DROP TABLE IF EXISTS census_findings20 CASCADE;
DROP TABLE IF EXISTS census_findings21 CASCADE;
DROP TABLE IF EXISTS census_findings22 CASCADE;
DROP TABLE IF EXISTS census_findingstext_formatted19 CASCADE;
DROP TABLE IF EXISTS census_findingstext_formatted20 CASCADE;
DROP TABLE IF EXISTS census_findingstext_formatted21 CASCADE;
DROP TABLE IF EXISTS census_findingstext_formatted22 CASCADE;
DROP TABLE IF EXISTS census_findingstext19 CASCADE;
DROP TABLE IF EXISTS census_findingstext20 CASCADE;
DROP TABLE IF EXISTS census_findingstext21 CASCADE;
DROP TABLE IF EXISTS census_findingstext22 CASCADE;
DROP TABLE IF EXISTS census_gen16 CASCADE;
DROP TABLE IF EXISTS census_gen17 CASCADE;
DROP TABLE IF EXISTS census_gen18 CASCADE;
DROP TABLE IF EXISTS census_gen19 CASCADE;
DROP TABLE IF EXISTS census_gen20 CASCADE;
DROP TABLE IF EXISTS census_gen21 CASCADE;
DROP TABLE IF EXISTS census_gen22 CASCADE;
DROP TABLE IF EXISTS census_notes19 CASCADE;
DROP TABLE IF EXISTS census_notes20 CASCADE;
DROP TABLE IF EXISTS census_notes21 CASCADE;
DROP TABLE IF EXISTS census_notes22 CASCADE;
DROP TABLE IF EXISTS census_passthrough16 CASCADE;
DROP TABLE IF EXISTS census_passthrough17 CASCADE;
DROP TABLE IF EXISTS census_passthrough18 CASCADE;
DROP TABLE IF EXISTS census_passthrough19 CASCADE;
DROP TABLE IF EXISTS census_passthrough20 CASCADE;
DROP TABLE IF EXISTS census_passthrough21 CASCADE;
DROP TABLE IF EXISTS census_passthrough22 CASCADE;
DROP TABLE IF EXISTS census_revisions19 CASCADE;
DROP TABLE IF EXISTS census_revisions20 CASCADE;
DROP TABLE IF EXISTS census_revisions21 CASCADE;
DROP TABLE IF EXISTS census_revisions22 CASCADE;
DROP TABLE IF EXISTS census_ueis22 CASCADE;
