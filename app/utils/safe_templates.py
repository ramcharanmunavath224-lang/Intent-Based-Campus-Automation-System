from fastapi.templating import Jinja2Templates

class _SafeCache(dict):
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except TypeError:
            raise KeyError

    def get(self, key, default=None):
        try:
            return super().get(key, default)
        except TypeError:
            return default

    def __setitem__(self, key, value):
        try:
            super().__setitem__(key, value)
        except TypeError:
            # ignore unhashable keys
            return


def get_templates(directory):
    """Return a Jinja2Templates instance with a safe cache that tolerates
    unhashable globals (avoids TypeError when Jinja2 tries to use request
    objects or dicts inside cache keys).
    """
    t = Jinja2Templates(directory=directory)
    t.env.cache = _SafeCache()
    return t
