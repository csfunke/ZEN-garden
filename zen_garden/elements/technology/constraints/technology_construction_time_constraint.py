"""Capacity commissioning constraint."""

import linopy as lp
import xarray as xr
from linopy.expressions import LinearExpression

from zen_garden.elements.technology.masks import CapacityAdditionEligibleMask
from zen_garden.model.component_types.constraint import GenericConstraint


class TechnologyConstructionTimeConstraint(GenericConstraint):
    """Link capacity additions to investments using construction lead time."""

    name = "constraint_technology_construction_time"
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
        lhs = lp.merge(
            [
                1 * optimization_model.variables["capacity_addition"],
                -optimization_model.expressions[
                    "capacity_additions_from_new_investments"
                ],
            ],
            compat="broadcast_equals",
            join="outer",
            cls=LinearExpression,
        )
        rhs = xr.align(
            lhs.const,
            optimization_model.expressions[
                "capacity_additions_from_pre_horizon_investments"
            ],
            join="left",
        )[1]
        return lhs == rhs
