"""Mask for CAPEX associated with committed capacity."""

from zen_garden.model.component_types.mask import GenericMask


class ExistingCapexMask(GenericMask):
    """Outstanding CAPEX from committed capacity, including future vintages."""

    name = "existing_capex"
    indices = ("set_technologies", "set_location", "set_years")

    @classmethod
    def get_mask(cls, model_constructor, registry):
        existing = model_constructor.optimization_model.parameters.existing_capex
        return existing.fillna(0) != 0
