from zen_garden.elements.technology.diffusion import existing_capacity_growth
from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromExistingCapacity(GenericExpression):
    """Capacity growth supported by depreciated pre-horizon capacity."""

    name = "capacity_growth_from_existing_capacity"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    units = "power or energy according to set_capacity_types"

    @classmethod
    def get_expression(cls, model_constructor):
        return existing_capacity_growth(model_constructor, include_spillovers=False)
