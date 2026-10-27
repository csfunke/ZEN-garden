from zen_garden.elements.technology.diffusion import previous_addition_growth
from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromLocalLearning(GenericExpression):
    """Capacity growth supported by depreciated additions at the same location."""

    name = "capacity_growth_from_local_learning"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    units = "power or energy according to set_capacity_types"

    @classmethod
    def get_expression(cls, model_constructor):
        return previous_addition_growth(model_constructor, include_spillovers=False)
