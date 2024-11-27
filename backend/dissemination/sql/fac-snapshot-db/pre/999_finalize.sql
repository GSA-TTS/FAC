-- PostgREST likes to know when the schemas and things
-- attached to them change.
NOTIFY pgrst, 'reload schema';
