from zen_garden.elements.technology.diffusion import storage_energy_diffusion_rate
from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromExistingCapacityEnergy(GenericExpression):
    """Storage energy growth supported by pre-horizon capacity."""

    name = "capacity_growth_from_existing_capacity_energy"
    indices = ("set_storage_technologies", "set_nodes", "set_years")

    @classmethod
    def get_expression(cls, model_constructor):
        r"""Construct learning from existing storage energy capacity.

        Summary:
            Measure growth supported by depreciated pre-horizon capacity.

        Formulation:

        .. math::

            d_{h,n,y}\sum_v e^{existing}_{h,n,v}
            (1-\delta_h)^{\Delta y(y-y_0)-1+\tau_h-\tau^{existing}_{h,n,v}}

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Storage energy growth supported by existing capacity.
        """
        model = model_constructor.optimization_model
        technologies = model.sets["set_storage_technologies"]
        interval = model.parameters.interval_between_years
        addition = model.variables["capacity_addition_energy"]
        years_from_start = interval * (
            addition.coords["set_years"] - model.sets["set_years"][0]
        )
        existing_lifetime = model.parameters.lifetime_existing.sel(
            set_technologies=technologies,
            set_location=model.sets["set_nodes"],
        ).rename(
            set_technologies="set_storage_technologies",
            set_location="set_nodes",
        )
        lifetime = model.parameters.lifetime.sel(set_technologies=technologies).rename(
            set_technologies="set_storage_technologies"
        )
        depreciation = model.parameters.knowledge_depreciation_rate
        factor = (1 - depreciation) ** (
            years_from_start - 1 + lifetime - existing_lifetime
        )
        factor = factor.where(lifetime >= existing_lifetime - years_from_start, 0)
        return storage_energy_diffusion_rate(model_constructor) * (
            model.parameters.capacity_existing_energy * factor
        ).sum("set_technologies_existing")
