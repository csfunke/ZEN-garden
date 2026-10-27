"""Energy-capacity additions for storage technologies."""

from zen_garden.model.component_types.expression import GenericExpression


class StorageEnergyCapacityAddition(GenericExpression):
    """Select storage energy-capacity additions."""

    name = "storage_energy_capacity_addition"
    indices = ("set_storage_technologies", "set_location", "set_years")

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            optimization_model.variables["capacity_addition"]
            .sel(
                set_technologies=optimization_model.sets["set_storage_technologies"],
                set_capacity_types="energy",
            )
            .rename({"set_technologies": "set_storage_technologies"})
        )
