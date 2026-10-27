"""Storage capacity available while the charging binary is active."""

from zen_garden.model.component_types.expression import GenericExpression


class ChargingModeCapacityLimit(GenericExpression):
    """Multiply storage power limit by the charging-mode binary."""

    name = "charging_mode_capacity_limit"
    indices = (
        "set_storage_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    units = "power"
    dependencies = ("storage_power_capacity_limit",)

    @classmethod
    def should_construct(cls, model_constructor):
        return model_constructor.config.system.storage_charge_discharge_binary and bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            optimization_model.variables["charge_storage_binary"]
            * optimization_model.expressions["storage_power_capacity_limit"]
        )
