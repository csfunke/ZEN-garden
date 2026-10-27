"""Installed-capacity upper-limit constraint."""

import numpy as np

from zen_garden.elements.technology.masks import CapacityAvailableMask
from zen_garden.model.component_types.constraint import GenericConstraint


class TechnologyCapacityLimitNotReachedConstraint(GenericConstraint):
    """Limit capacity where existing assets remain below a finite limit."""

    name = "constraint_technology_capacity_limit_not_reached"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    masks = (CapacityAvailableMask,)

    @classmethod
    def get_constraint(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        limit = optimization_model.parameters.capacity_limit
        selected = (limit != np.inf) & optimization_model.expressions[
            "existing_capacity_is_below_limit"
        ]
        return optimization_model.variables["capacity"].where(selected) <= limit.where(
            selected, 0.0
        )
