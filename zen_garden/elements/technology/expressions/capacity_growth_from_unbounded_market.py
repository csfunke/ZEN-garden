import pandas as pd

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

    @staticmethod
    def _class_technologies(model_constructor, technology):
        """Return technologies belonging to the same concrete element class."""
        model = model_constructor.optimization_model
        element = model_constructor.element_registry.get_element_by_name(technology)
        if element is None:
            raise ValueError(f"Element {technology} not found")
        return model.sets[element.label]

    @classmethod
    def get_expression(cls, model_constructor):
        model = model_constructor.optimization_model
        capacity_previous = model.variables["capacity_previous"]
        shares = {
            (technology, other): (
                model.parameters.market_share_unbounded
                if other != technology
                and model.sets["set_reference_carriers"][technology][0]
                == model.sets["set_reference_carriers"][other][0]
                else 0
            )
            for technology in model.sets["set_technologies"]
            for other in cls._class_technologies(model_constructor, technology)
        }
        shares = pd.Series(shares)
        shares.index.names = ["set_technologies", "set_other_technologies"]
        shares = shares.to_xarray().broadcast_like(capacity_previous.lower).fillna(0)
        return (
            (
                shares
                * capacity_previous.rename(
                    {"set_technologies": "set_other_technologies"}
                )
            )
            .where(shares != 0)
            .sum("set_other_technologies")
        )
