"""Capacity-addition restriction at reached capacity limits."""

import numpy as np

from zen_garden.elements.technology.masks import CapacityAdditionEligibleMask
from zen_garden.model.component_types.constraint import GenericConstraint


class TechnologyCapacityLimitReachedConstraint(GenericConstraint):
    """Prevent additions where existing capacity already reaches the limit."""

    name = "constraint_technology_capacity_limit_reached"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    masks = (CapacityAdditionEligibleMask,)

    @classmethod
    def get_constraint(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        additions = optimization_model.variables["capacity_addition"]
        if not model_constructor.config.system.allow_investment:
            return additions == 0
        limit = optimization_model.parameters.capacity_limit
        selected = (limit != np.inf) & ~optimization_model.expressions[
            "existing_capacity_is_below_limit"
        ]
        return additions.where(selected) == 0
