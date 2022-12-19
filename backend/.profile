# We only want to run migrate and collecstatic for the first app instance, not
# for additional app instances, so we gate all of this behind CF_INSTANCE_INDEX
# being 0.
[ "$CF_INSTANCE_INDEX" = 0 ] && echo 'Starting .profile' &&
python manage.py migrate &&
echo 'Finished migrate' &&
echo 'Starting collectstatic' &&
python manage.py collectstatic --noinput &&
echo 'Finished collectstatic, finished .profile'
