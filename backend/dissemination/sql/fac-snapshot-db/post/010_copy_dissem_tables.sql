---------------------------------------------
-- COPY DISSEMINATION TABLES
-- WHY? Because our deploy process will want to make backups,
-- we will want to DROP and recreate those tables. If we 
-- point our API at those tables (even in fac-snapshot-db), we 
-- will have a problem at deploy-time.
--
-- So, the fix is to take the copy that is in fac-snapshot-db (the 
-- actual snapshot of the prod data) and make *one more copy*. We will
-- then point the API at that. We do this becasue we can (nightly) drop
-- the copy, tear down the API, make a fresh backup (and copy) and then
-- stand the API back up.
--
-- It is a long way to go, but it kinda makes our entire data pipeline 
-- "stateless," in a way.

-- CREATE TABLE [Table to copy To]
-- AS [Table to copy From]

CREATE OR REPLACE FUNCTION copy.create_copy_of_dissemination()
  RETURNS VOID
AS
$ct$
BEGIN
  CREATE TABLE copy.dissemination_additionalein
  AS TABLE public.dissemination_additionalein;

  CREATE TABLE copy.dissemination_additionaluei
  AS TABLE public.dissemination_additionaluei;

  CREATE TABLE copy.dissemination_captext
  AS TABLE public.dissemination_captext;

  CREATE TABLE copy.dissemination_federalaward
  AS TABLE public.dissemination_federalaward;

  CREATE TABLE copy.dissemination_finding
  AS TABLE public.dissemination_finding;

  CREATE TABLE copy.dissemination_findingtext
  AS TABLE public.dissemination_findingtext;

  CREATE TABLE copy.dissemination_general
  AS TABLE public.dissemination_general;

  CREATE TABLE copy.dissemination_invalidauditrecord
  AS TABLE public.dissemination_invalidauditrecord;

  CREATE TABLE copy.dissemination_issuedescriptionrecord
  AS TABLE public.dissemination_issuedescriptionrecord;

  CREATE TABLE copy.dissemination_migrationinspectionrecord
  AS TABLE public.dissemination_migrationinspectionrecord;

  CREATE TABLE copy.dissemination_note
  AS TABLE public.dissemination_note;

  CREATE TABLE copy.dissemination_passthrough
  AS TABLE public.dissemination_passthrough;

  CREATE TABLE copy.dissemination_secondaryauditor
  AS TABLE public.dissemination_secondaryauditor;
END
$ct$
LANGUAGE plpgsql;

DO LANGUAGE plpgsql
$GATE$
    DECLARE
        the_schema varchar := 'copy';
        the_table  varchar := 'dissemination_general';
    BEGIN
        IF EXISTS (
            SELECT FROM pg_tables
            WHERE  schemaname = the_schema
            AND    tablename  = the_table
            )
        THEN
          RAISE info 'We have a copy of dissem in fac-snapshot, so no need to make another.';
        ELSE
          RAISE info 'Making a copy of dissemination_* in fac-snapshot.';
          PERFORM copy.create_copy_of_dissemination();
        END IF;
    END
$GATE$;

