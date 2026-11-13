from django.core.cache import cache
from django.core.paginator import Paginator, Page
from django.utils.functional import cached_property
import logging

logger = logging.getLogger(__name__)


class CachedPaginator(Paginator):

    def __init__(self, object_list, per_page, pg_cache_key, cnt_cache_key, **kwargs):
        """Initialize method needs cache keys."""
        super().__init__(object_list, per_page, **kwargs)
        self.pg_cache_key = pg_cache_key
        self.cnt_cache_key = cnt_cache_key

    def page(self, number):
        """Validate the page number natively (handles invalid/empty pages)."""
        number = self.validate_number(number)

        try:
            logger.info(f"CACHE: READ from cache key: {self.pg_cache_key}")

            cached_object_list = cache.get(self.pg_cache_key)

            if cached_object_list is None:
                # fetch from db and convert QuerySet to a standard list to evaluate
                logger.info(
                    f"CACHE: WRITE 'page result list' to cache key: {self.pg_cache_key}"
                )

                actual_page = super().page(number)
                cached_object_list = list(actual_page.object_list)
                cache.set(self.pg_cache_key, cached_object_list)
        except Exception as e:
            # fail silently
            logger.error(f"CACHE: FAIL for 'page result list' during read/write: {e}")

        # reconstruct and return a valid page object
        return Page(cached_object_list, number, self)

    @cached_property
    def count(self):
        """Return total number of objects, using our cache backend first."""
        try:
            logger.info(f"CACHE: READ from cache key: {self.cnt_cache_key}")

            result_count = cache.get(self.cnt_cache_key)

            if result_count is None:
                # fetch count from super class
                logger.info(
                    f"CACHE: WRITE 'count (results_count)' to cache key: {self.cnt_cache_key}"
                )

                result_count = lambda: super(CachedPaginator, self).count
                cache.set(self.cnt_cache_key, result_count)
        except AttributeError as e:
            # fail silently
            logger.error(
                f"CACHE: FAIL for 'count (results_count)' during READ/WRITE: {e}"
            )

        return result_count
