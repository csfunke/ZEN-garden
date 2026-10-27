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
        """Construct allow discharging only while the storage charging mode is inactive.

        Summary:
            Allow discharging only while the storage charging mode is inactive.

        Formulation:

        .. math::

            F^{dis}+\\bar k^{power}B^{ch}\\leq\\bar k^{power}

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        model = model_constructor.optimization_model
        return (
            model.variables["flow_storage_discharge"]
            + model.expressions["charging_mode_capacity_limit"]
            <= model.expressions["storage_power_capacity_limit"]
        )
