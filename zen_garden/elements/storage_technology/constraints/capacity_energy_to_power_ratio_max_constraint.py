import numpy as np

from zen_garden.elements.technology.masks import CapacityAdditionAnyTypeMask
from zen_garden.model.component_types.constraint import GenericConstraint


class CapacityEnergyToPowerRatioMaxConstraint(GenericConstraint):
    """Enforce the maximum energy-to-power ratio of storage additions."""

    name = "constraint_capacity_energy_to_power_ratio_max"
    indices = ("set_storage_technologies", "set_location", "set_years")
    masks = (CapacityAdditionAnyTypeMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        ratio = model.parameters.energy_to_power_ratio_max
        mask = ratio != np.inf
        return model.expressions["storage_energy_capacity_addition"].where(mask) <= (
            ratio * model.expressions["storage_power_capacity_addition"]
        ).where(mask)
