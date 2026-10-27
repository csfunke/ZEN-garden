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
    units = "energy"

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_expression(cls, model_constructor):
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
