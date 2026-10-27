"""Storage-level change after standing losses."""

from zen_garden.elements.storage_technology.storage_time import (
    get_previous_storage_time_step_arrays,
)
from zen_garden.model.component_types.expression import GenericExpression


class StorageLevelChangeAfterSelfDischarge(GenericExpression):
    """Compare storage level with the decayed predecessor level."""

    name = "storage_level_change_after_self_discharge"
    indices = (
        "set_storage_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours_storage",
    )

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct compare storage level with the decayed predecessor level.

        Summary:
            Compare storage level with the decayed predecessor level.

        Formulation:

        .. math::

            L_{h,n,y,r}(1-\\lambda^{self}_{h,n,y})^{\\tau_r}-L_{h,n,y,\\pi(r)}

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Expression over its declared model indices.
        """
        optimization_model = model_constructor.optimization_model
        previous_year, previous_hour, coupling_mask = (
            get_previous_storage_time_step_arrays(model_constructor)
        )
        self_discharge = optimization_model.parameters.self_discharge
        duration = optimization_model.parameters.duration_representative_hours_storage
        storage_level = optimization_model.variables["storage_level"]
        previous_level = storage_level.sel(
            set_years=previous_year,
            set_representative_hours_storage=previous_hour,
        )
        change = storage_level - (1 - self_discharge) ** duration * previous_level
        return change.where(coupling_mask, 0.0)
