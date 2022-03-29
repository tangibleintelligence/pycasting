from collections import defaultdict
from datetime import timedelta
from typing import Dict, Callable

from pycasting.predicting.misc import PredictorCategory

_predictor_registry: Dict[PredictorCategory, Dict[str, Callable]] = defaultdict(defaultdict)


def predictor(category: PredictorCategory, name: str):
    def with_register(fn):
        _predictor_registry[category][name] = fn

        return fn

    return with_register


def predict(category: PredictorCategory, name: str, offset: timedelta, **params):
    predictor_fn = _predictor_registry.get(category, {}).get(name, None)
    if predictor_fn is None:
        raise ValueError(f"No matching predictor: {category} | {name}")

    return predictor_fn(offset, **params)
