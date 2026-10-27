import numpy as np

from zen_garden.elements.technology.masks import InvestmentEligibleMask
from zen_garden.model.component_types.variable import GenericVariable


class CapacityInvestment(GenericVariable):
    """Variable for invested technology capacity."""

    name = "capacity_investment"
    symbol = r"\Delta K^{\mathrm{inv}}_{h,p,y}"
    indices = ["set_technologies", "set_capacity_types", "set_location", "set_years"]
    doc = "Size of invested technology h at location p and period y."
    unit_category = {"energy_quantity": 1, "time": -1}
    masks = [InvestmentEligibleMask]

    @classmethod
    def get_bounds(cls, model_constructor, index_sets):
        return 0, np.inf
