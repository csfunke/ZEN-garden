from zen_garden.elements.technology.diffusion import (
    diffusion_rate,
    technology_type_mask,
)
from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromExistingCapacityWithSpillovers(GenericExpression):
    """Capacity growth supported by existing capacity with location spillovers."""

    name = "capacity_growth_from_existing_capacity_with_spillovers"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )

    @classmethod
    def should_construct(cls, model_constructor):
        return (
            model_constructor.optimization_model.parameters.knowledge_spillover_rate
            != float("inf")
        )

    @classmethod
    def get_expression(cls, model_constructor):
        model = model_constructor.optimization_model
        interval = model_constructor.config.system.interval_between_years
        capacity_addition = model.variables["capacity_addition"]
        capacity_existing = model.parameters.capacity_existing
        years_from_start = interval * (
            capacity_addition.coords["set_years"] - model.sets["set_years"][0]
        )
        lifetime_existing = model.parameters.lifetime_existing
        lifetime = model.parameters.lifetime
        depreciation = model.parameters.knowledge_depreciation_rate
        factor = (1 - depreciation) ** (
            years_from_start - 1 + lifetime - lifetime_existing
        )
        factor = factor.where(lifetime >= lifetime_existing - years_from_start, 0)
        spillover_rate = model.parameters.knowledge_spillover_rate
        capacity_existing = capacity_existing + spillover_rate * (
            capacity_existing.sum("set_location") - capacity_existing
        ).where(technology_type_mask(model_constructor), 0)
        return diffusion_rate(model_constructor) * (capacity_existing * factor).sum(
            "set_technologies_existing"
        )
