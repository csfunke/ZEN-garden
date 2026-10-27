"""Power-capacity limit for storage operation."""

from zen_garden.model.component_types.expression import GenericExpression


class StoragePowerCapacityLimit(GenericExpression):
    """Select and align storage power-capacity limits."""

    name = "storage_power_capacity_limit"
    indices = ("set_storage_technologies", "set_nodes", "set_years")

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return optimization_model.parameters.capacity_limit.rename(
            {
                "set_technologies": "set_storage_technologies",
                "set_location": "set_nodes",
            }
        ).sel(
            set_storage_technologies=optimization_model.sets[
                "set_storage_technologies"
            ],
            set_nodes=optimization_model.sets["set_nodes"],
            set_capacity_types="power",
        )
