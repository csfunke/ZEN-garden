"""Operational mask derived from available power capacity."""

from zen_garden.elements.technology.masks.capacity_available_mask import (
    CapacityAvailableMask,
)
from zen_garden.model.component_types.mask import GenericMask


class PowerOperationMask(GenericMask):
    """Technology power capacity available in each operational time step."""

    name = "power_operation"
    dependencies = [CapacityAvailableMask]

    @classmethod
    def build(cls, model_constructor, registry):
        capacity = registry[CapacityAvailableMask].sel(set_capacity_types="power")
        capacity = capacity.drop_vars("set_capacity_types", errors="ignore")
        representative_hours = list(
            model_constructor.optimization_model.sets["set_representative_hours"]
        )
        return capacity.expand_dims(
            {"set_representative_hours": representative_hours}, axis=-1
        )
