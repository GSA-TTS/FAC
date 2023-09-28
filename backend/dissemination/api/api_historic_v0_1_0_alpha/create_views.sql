begin;
select 1;
commit;

notify pgrst, 'reload schema';
