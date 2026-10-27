"""Capacity commissioned from decisions inside the modeled horizon."""

from zen_garden.elements.technology.construction_time import (
    get_investment_time_mapping,
)
from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.model.linear_expression import transpose_linear_expression


class CapacityAdditionsFromNewInvestments(GenericExpression):
    """Map modeled investment decisions to their commissioning years."""

    name = "capacity_additions_from_new_investments"
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
        addition = optimization_model.variables["capacity_addition"]
        investment = optimization_model.variables["capacity_investment"]
        mapping = get_investment_time_mapping(model_constructor)
        current = mapping[
            mapping.index.get_level_values("set_time_steps_construction").isin(
                optimization_model.sets["set_years"]
            )
        ]
        current = current.to_xarray().broadcast_like(investment.mask).fillna(0)
        current = current.transpose(*addition.dims, "set_time_steps_construction")
        investment = investment.rename(
            {"set_years": "set_time_steps_construction"}
        ).broadcast_like(current)
        investment = transpose_linear_expression(1 * investment, current.dims)
        return (current * investment).sum("set_time_steps_construction")
