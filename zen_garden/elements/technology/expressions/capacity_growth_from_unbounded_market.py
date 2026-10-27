from zen_garden.elements.technology.diffusion import unbounded_market_growth
from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromUnboundedMarket(GenericExpression):
    """Capacity growth supported by peers serving the same reference carrier."""

    name = "capacity_growth_from_unbounded_market"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    units = "power or energy according to set_capacity_types"

    @classmethod
    def get_expression(cls, model_constructor):
        return unbounded_market_growth(model_constructor)
