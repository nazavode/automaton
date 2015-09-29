# -*- coding: utf-8 -*-



__all__ = (
    "classproperty"
)


class classproperty(object):  # pylint: disable=invalid-name, too-few-public-methods
    """ Class property, to be used as a static, getter-only property. """

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, cls):
        return self.func(cls)