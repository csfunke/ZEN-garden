import numpy as np
import xarray as xr

from zen_garden.elements.storage_technology.masks._utils import canonical_storage_array
from zen_garden.model.component_types.mask import GenericMask


class EnergyInstallationRelevantMask(GenericMask):
    """Storage energy installation binaries with a nonzero model role."""

    name = "energy_installation_relevant"
    indices = ("set_technologies", "set_location", "set_years")

    @classmethod
    def get_mask(cls, model_constructor, registry):
        model = model_constructor.optimization_model
        limit = canonical_storage_array(model.parameters.capacity_limit_energy)
        minimum = canonical_storage_array(model.parameters.capacity_addition_min_energy)
        maximum = canonical_storage_array(model.parameters.capacity_addition_max_energy)
        mask = xr.zeros_like(limit, dtype=bool)
        mask |= minimum.notnull() & (minimum != 0)
        mask |= maximum.notnull() & np.isfinite(maximum) & (maximum != 0)
        return mask
