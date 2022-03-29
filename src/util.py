"""Misc Utility functions"""


def all_subclasses(cls: type):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])
