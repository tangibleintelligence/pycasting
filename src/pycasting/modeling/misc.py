import pydantic.json
from uncertainties.core import Variable, ufloat_fromstr

# noinspection PyUnresolvedReferences
class UFloat(Variable):
    """A float with uncertainty."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return ufloat_fromstr(v)
        elif isinstance(v, Variable):
            return v
        else:
            raise ValueError("must be a str or a ufloat")

    # No-ops to make code completion more happy
    def __add__(self, other):
        return super().__add__(other)

    def __radd__(self, other):
        return super().__radd__(other)

    def __mul__(self, other):
        return super().__mul__(other)

    def __rmul__(self, other):
        return super().__rmul__(other)

    def __pow__(self, power, modulo=None):
        return super().__pow__(power, modulo)

    def __rpow__(self, other):
        return super().__rpow__(other)

    def __truediv__(self, other):
        return super().__truediv__(other)

    def __rtruediv__(self, other):
        return super().__rtruediv__(other)

    def __lt__(self, other):
        return super().__lt__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __le__(self, other):
        return super().__le__(other)

    def __ge__(self, other):
        return super().__ge__(other)


pydantic.json.ENCODERS_BY_TYPE[Variable] = lambda v: str(v)
