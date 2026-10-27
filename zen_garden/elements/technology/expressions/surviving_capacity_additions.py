"""Capacity additions that remain within their technical lifetime."""

import itertools

import pandas as pd

from zen_garden.elements.technology.lifetime import get_active_vintage_years
from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.model.linear_expression import transpose_linear_expression


class SurvivingCapacityAdditions(GenericExpression):
    """Sum modeled capacity vintages that have not retired."""

    name = "surviving_capacity_additions"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    units = "power or energy according to set_capacity_types"

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        capacity = optimization_model.variables["capacity"]
        active_vintages = pd.MultiIndex.from_tuples(
            [
                (technology, year, vintage)
                for technology, year in itertools.product(
                    optimization_model.sets["set_technologies"],
                    optimization_model.sets["set_years"],
                )
                for vintage in get_active_vintage_years(
                    model_constructor, technology, year
                )
            ],
            names=["set_technologies", "set_years", "set_years_prev"],
        )
        active = pd.Series(1, index=active_vintages).to_xarray()
        active = active.broadcast_like(capacity.lower).fillna(0)
        active = active.transpose(*capacity.dims, "set_years_prev")
        additions = optimization_model.variables["capacity_addition"].rename(
            {"set_years": "set_years_prev"}
        )
        additions = transpose_linear_expression(
            1 * additions.broadcast_like(active), active.dims
        )
        return (active * additions).sum("set_years_prev")
