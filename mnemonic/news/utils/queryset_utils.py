from collections import defaultdict
from django.db import models


class CachedManager(models.Manager):
    use_in_migrations = True

    def __init__(self, *args, **kwargs):
        super(CachedManager, self).__init__(*args, **kwargs)
        self._cache = defaultdict(dict)

    def clear_cache(self):
        self._cache.clear()

    def get_cached(self, **kwargs):
        key, value = next(iter(kwargs.items()))
        try:
            obj = self._cache[self.db][value]
        except KeyError:
            obj = self.get(**kwargs)
            self._cache[self.db][key] = obj
        return obj
