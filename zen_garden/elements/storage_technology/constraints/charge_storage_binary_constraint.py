from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.model.component_types.constraint import GenericConstraint


class ChargeStorageBinaryConstraint(GenericConstraint):
    """Allow charging only while the storage charging mode is active."""

    name = "constraint_charge_storage_binary"
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
            model.variables["flow_storage_charge"]
            <= model.expressions["charging_mode_capacity_limit"]
        )
