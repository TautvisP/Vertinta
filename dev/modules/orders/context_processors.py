from .utils import memoize
from .enums import ObjectTypes


# This function is used to pass the object types to all templates without having to pass them explicitly in each view.
def object_types(request):
    return {
        "land": memoize(
            lambda: ObjectTypes.LAND_TYPE
        ),
        "apartament": memoize(
            lambda: ObjectTypes.APARTAMENT_TYPE
        ),
        "house": memoize(
            lambda: ObjectTypes.HOUSE_TYPE
        ),
        "garden": memoize(
            lambda: ObjectTypes.GARDEN_TYPE
        ),
        "cottage": memoize(
            lambda: ObjectTypes.COTTAGE_TYPE
        ),
        "other": memoize(
            lambda: ObjectTypes.OTHER_TYPE
        ),
        "garage": memoize(
            lambda: ObjectTypes.GARAGE_TYPE
        ),
        "storage": memoize(
            lambda: ObjectTypes.STORAGE
        ),
        "arbor": memoize(
            lambda: ObjectTypes.ARBOR
        )
        #"industrial": memoize(
        #    lambda: ObjectTypes.INDUSTRIAL_TYPE
        #),
        #"culture": memoize(
        #    lambda: ObjectTypes.CULTURE_TYPE
        #),
        #"science": memoize(
        #    lambda: ObjectTypes.EDUCATION_TYPE
        #),
        #"relax": memoize(
        #    lambda: ObjectTypes.RELAXATION_TYPE
        #),
        #"pool": memoize(
        #    lambda: ObjectTypes.POOL
        #)
    }
