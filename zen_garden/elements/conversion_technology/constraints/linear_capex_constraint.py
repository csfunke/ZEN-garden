import numpy as np

from zen_garden.elements.technology.masks import PowerCapacityAdditionMask
from zen_garden.model.component_types.constraint import GenericConstraint


class LinearCapexConstraint(GenericConstraint):
    """Set conversion overnight CAPEX from power-capacity additions."""

    name = "constraint_linear_capex"
    indices = ("set_technologies", "set_location", "set_years")
    masks = (PowerCapacityAdditionMask,)

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        technologies = model.sets["set_conversion_technologies"]
        nodes = model.sets["set_nodes"]
        cost = model.variables["cost_capex_overnight"].sel(
            set_technologies=technologies,
            set_capacity_types="power",
            set_location=nodes,
        )
        specific = model.parameters.capex_specific_conversion.rename(
            {
                old: new
                for old, new in zip(
                    model.parameters.capex_specific_conversion.dims,
                    ["set_technologies", "set_location", "set_years"],
                    strict=False,
                )
            }
        ).broadcast_like(cost.lower)
        mask = ~np.isnan(specific)
        return cost.where(mask) == model.expressions["conversion_overnight_capex"]
