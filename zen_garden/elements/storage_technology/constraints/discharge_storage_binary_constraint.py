from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.model.component_types.constraint import GenericConstraint


class DischargeStorageBinaryConstraint(GenericConstraint):
    """Allow discharging only while the storage charging mode is inactive."""

    name = "constraint_discharge_storage_binary"
    indices = (
        "set_storage_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    masks = (PowerOperationMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        return model_constructor.config.system.storage_charge_discharge_binary and bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        return (
            model.variables["flow_storage_discharge"]
            + model.expressions["charging_mode_capacity_limit"]
            <= model.expressions["storage_power_capacity_limit"]
        )
