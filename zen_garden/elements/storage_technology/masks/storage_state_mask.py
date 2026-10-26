"""Mask for storage state variables and constraints."""

from zen_garden.elements.storage_technology.masks.storage_inflow_mask import (
    StorageInflowMask,
)
from zen_garden.elements.technology.masks import CapacityAnyTypeMask
from zen_garden.model.component_types.mask import GenericMask


class StorageStateMask(GenericMask):
    """Storage states required for a year containing capacity or inflow."""

    name = "storage_state"
    dependencies = [CapacityAnyTypeMask, StorageInflowMask]

    @classmethod
    def build(cls, model_constructor, registry):
        model = model_constructor.optimization_model
        available = registry[CapacityAnyTypeMask]
        inflow = registry[StorageInflowMask]
        storage_technologies = list(model.sets["set_storage_technologies"])
        nodes = list(model.sets["set_nodes"])
        index_values, index_names = model_constructor.create_custom_set(
            [
                "set_storage_technologies",
                "set_nodes",
                "set_years",
                "set_representative_hours_storage",
            ]
        )
        valid_storage_hours = model.sets.indices_to_mask(
            index_values, index_names, (0, 0)
        )[0].rename(
            {
                "set_storage_technologies": "set_technologies",
                "set_nodes": "set_location",
            }
        )
        year_active = available.sel(
            set_technologies=storage_technologies,
            set_location=nodes,
        ) | inflow.any("set_representative_hours")
        return valid_storage_hours & year_active
