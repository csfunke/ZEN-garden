from zen_garden.elements.technology.diffusion import diffusion_rate
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
        return diffusion_rate(model_constructor) * (capacity_existing * factor).sum(
            "set_technologies_existing"
        )
