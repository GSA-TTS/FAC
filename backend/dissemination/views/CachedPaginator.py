from django.core.cache import cache
from django.core.paginator import Paginator, Page
from django.utils.functional import cached_property
import logging

logger = logging.getLogger(__name__)


class CachedPaginator(Paginator):

    def __init__(self, object_list, per_page, pg_cache_key, cnt_cache_key, **kwargs):
        super().__init__(object_list, per_page, **kwargs)
        self.pg_cache_key = pg_cache_key
        self.cnt_cache_key = cnt_cache_key

    def page(self, number):
        # validate the page number natively (handles invalid/empty pages)
        number = self.validate_number(number)

        # try to hit the cache
        try:
            logger.info(f"CACHE: pulling from cache for: {self.pg_cache_key}")
            cached_object_list = cache.get(self.pg_cache_key)
            if cached_object_list is None:
                # cache miss: fetch from db and convert QuerySet to a standard list to evaluate it
                logger.info(
                    f"CACHE: cache miss - adding 'page list' to cache for: {self.pg_cache_key}"
                )
                actual_page = super().page(number)
                cached_object_list = list(actual_page.object_list)

                # store the evaluated list in cache
                cache.set(self.pg_cache_key, cached_object_list)
        except Exception as e:
            # fail silently
            logger.error(
                f"CACHE: cache connection failed for the 'cached page list' during read/write: {e}"
            )
            # we'll to add feature flags to workaround a misbehaving cache server

        # reconstruct and return a valid page object
        return Page(cached_object_list, number, self)

    @cached_property
    def count(self):
        """
        Returns the total number of objects, looking across the cache backend first.
        """
        try:
            logger.info(f"CACHE: pulling from cache for: {self.cnt_cache_key}")
            result_count = cache.get(self.cnt_cache_key)

            if result_count is None:
                # cache miss: fetch from db and convert QuerySet to a standard list to evaluate it
                logger.info(
                    f"CACHE: cache miss - adding 'page list' to cache for: {self.cnt_cache_key}"
                )

                result_count = lambda: super(CachedPaginator, self).count

                # store the evaluated list in cache
                cache.set(self.cnt_cache_key, result_count)
        except AttributeError as e:
            # fail silently
            logger.error(
                f"CACHE: cache connection failed for the 'cached page list' during read/write: {e}"
            )

        # Attempt to retrieve cached count or evaluate the DB query if missing
        return result_count
        # return cache.get_or_set(self.cnt_cache_key, lambda: super(CachedPaginator, self).count)
