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

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_additionalein()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_additionalein
    AS SELECT * FROM public.dissemination_additionalein;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_additionaluei()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_additionaluei
    AS SELECT * FROM public.dissemination_additionaluei;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_captext()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_captext
    AS SELECT * FROM public.dissemination_captext;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_federalaward()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_federalaward
    AS SELECT * FROM public.dissemination_federalaward;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_finding()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_finding
    AS SELECT * FROM public.dissemination_finding;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_findingtext()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_findingtext
    AS SELECT * FROM public.dissemination_findingtext;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_general()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_general
    AS SELECT * FROM public.dissemination_general;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_invalidauditrecord()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_invalidauditrecord
    AS SELECT * FROM public.dissemination_invalidauditrecord;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_migrationinspectionrecord()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_migrationinspectionrecord
    AS SELECT * FROM public.dissemination_migrationinspectionrecord;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_note()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_note
    AS SELECT * FROM public.dissemination_note;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_passthrough()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_passthrough
    AS SELECT * FROM public.dissemination_passthrough;
  END
  $ct$
  LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dissem_copy.create_dissemination_secondaryauditor()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE dissem_copy.dissemination_secondaryauditor
    AS SELECT * FROM public.dissemination_secondaryauditor;
  END
  $ct$
  LANGUAGE plpgsql;

DO LANGUAGE plpgsql
$go$
    BEGIN
      RAISE info 'create_dissemination_additionalein';
      PERFORM dissem_copy.create_dissemination_additionalein();
      RAISE info 'create_dissemination_additionaluei';
      PERFORM dissem_copy.create_dissemination_additionaluei();
      RAISE info 'create_dissemination_captext';
      PERFORM dissem_copy.create_dissemination_captext();
      RAISE info 'create_dissemination_federalaward';
      PERFORM dissem_copy.create_dissemination_federalaward();
      RAISE info 'create_dissemination_finding';
      PERFORM dissem_copy.create_dissemination_finding();
      RAISE info 'create_dissemination_findingtext';
      PERFORM dissem_copy.create_dissemination_findingtext();
      RAISE info 'create_dissemination_general';
      PERFORM dissem_copy.create_dissemination_general();
      RAISE info 'create_dissemination_invalidauditrecord';
      PERFORM dissem_copy.create_dissemination_invalidauditrecord();
      RAISE info 'create_dissemination_migrationinspectionrecord';
      PERFORM dissem_copy.create_dissemination_migrationinspectionrecord();
      RAISE info 'create_dissemination_note';
      PERFORM dissem_copy.create_dissemination_note();
      RAISE info 'create_dissemination_passthrough';
      PERFORM dissem_copy.create_dissemination_passthrough();
      RAISE info 'create_dissemination_secondaryauditor';
      PERFORM dissem_copy.create_dissemination_secondaryauditor();
    END
$go$;

