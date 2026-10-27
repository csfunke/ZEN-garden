from zen_garden.elements.technology.diffusion import previous_addition_growth
from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromSpillovers(GenericExpression):
    """Capacity growth supported by local and cross-location installation knowledge."""

    name = "capacity_growth_from_spillovers"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    units = "power or energy according to set_capacity_types"

    @classmethod
    def should_construct(cls, model_constructor):
        return (
            model_constructor.optimization_model.parameters.knowledge_spillover_rate
            != float("inf")
        )

    @classmethod
    def get_expression(cls, model_constructor):
        return previous_addition_growth(model_constructor, include_spillovers=True)
