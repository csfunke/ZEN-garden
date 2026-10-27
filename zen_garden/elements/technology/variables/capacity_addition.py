import numpy as np

from zen_garden.elements.technology.masks import CapacityAdditionEligibleMask
from zen_garden.model.component_types.variable import GenericVariable


class CapacityAddition(GenericVariable):
    """Variable for built/added technology capacity."""

    name = "capacity_addition"
    symbol = r"\Delta K_{h,p,y}"
    indices = ["set_technologies", "set_capacity_types", "set_location", "set_years"]
    doc = (
        "Size of built technology h (invested capacity after construction) at "
        "location p and period y."
    )
    unit_category = {"energy_quantity": 1, "time": -1}
    masks = [CapacityAdditionEligibleMask]

    @classmethod
    def get_bounds(cls, model_constructor, index_sets):
        return 0, np.inf
