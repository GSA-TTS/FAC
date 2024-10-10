--
-- This drops all the views, too.
---
DROP SCHEMA IF EXISTS public_api_v1_0_0 CASCADE;
DROP SCHEMA IF EXISTS public_api_v1_0_0_functions CASCADE;

notify pgrst,
       'reload schema';
