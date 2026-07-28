"""Request-scoped context (`g`) backed by a contextvar.

Standalone (no heavy imports) so it can be shared by fastapi_glue and the
shared utils (validators, dea) without a circular import. Replaces flask.g."""
import contextvars

_gctx: contextvars.ContextVar = contextvars.ContextVar("gms_g", default=None)


class _G:
    """Minimal flask.g replacement: g.x, g['x'], 'x' in g, g.get(), g.setdefault()."""

    def _store(self) -> dict:
        d = _gctx.get()
        if d is None:
            d = {}
            _gctx.set(d)
        return d

    def reset(self):
        _gctx.set({})

    def __getattr__(self, name):
        try:
            return self._store()[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self._store()[name] = value

    def __contains__(self, name):
        return name in self._store()

    def __getitem__(self, name):
        return self._store()[name]

    def __setitem__(self, name, value):
        self._store()[name] = value

    def get(self, name, default=None):
        return self._store().get(name, default)

    def setdefault(self, name, default=None):
        return self._store().setdefault(name, default)


g = _G()
