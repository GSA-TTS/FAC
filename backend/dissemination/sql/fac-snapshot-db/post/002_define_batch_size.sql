-- The batch_size is used to determine how many rows of data
-- are available in a single download. The PostgREST limit is 
-- (as of 20241024) set to 20K rows. Howwever, we could make our 
-- batches smaller. (This doesn't make things better, BTW.) So,
-- we set our batch size to the same size as the PgREST limit.
-- As a result, public tables are created with a batch number column, 
-- and that batch number is incremented as DIV(n, batch_size()).
-- 
-- This is defined as a function because there is no good way to define
-- a constant in Postgres/SQL.
-- https://stackoverflow.com/questions/13316773/is-there-a-way-to-define-a-named-constant-in-a-postgresql-query

CREATE OR REPLACE FUNCTION public.batch_size()
  RETURNS INT
  LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
'SELECT 20000';
