"""Capacity-limit headroom indicator."""

from zen_garden.model.component_types.expression import GenericExpression


class ExistingCapacityIsBelowLimit(GenericExpression):
    """Indicate where existing capacity is below the configured upper limit."""

    name = "existing_capacity_is_below_limit"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )

    @classmethod
    def get_expression(cls, model_constructor):
        parameters = model_constructor.optimization_model.parameters
        return parameters.existing_capacities < parameters.capacity_limit
