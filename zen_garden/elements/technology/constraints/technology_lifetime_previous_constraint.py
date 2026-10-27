"""Beginning-of-year available-capacity constraint."""

import linopy as lp
import xarray as xr
from linopy.expressions import LinearExpression

from zen_garden.elements.technology.masks import CapacityAvailableMask
from zen_garden.model.component_types.constraint import GenericConstraint


class TechnologyLifetimePreviousConstraint(GenericConstraint):
    """Define capacity before additions made in the current year."""

    name = "constraint_technology_lifetime_previous"
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
        lhs = lp.merge(
            [
                1 * optimization_model.variables["capacity_previous"],
                -optimization_model.expressions["surviving_capacity_additions"],
                1 * optimization_model.variables["capacity_addition"],
            ],
            compat="broadcast_equals",
            join="outer",
            cls=LinearExpression,
        )
        rhs = xr.align(
            lhs.const,
            optimization_model.parameters.existing_capacities,
            join="left",
        )[1]
        return lhs == rhs
