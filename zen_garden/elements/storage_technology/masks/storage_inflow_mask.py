"""Mask for nonzero exogenous storage inflow."""

import xarray as xr

from zen_garden.model.component_types.mask import GenericMask


class StorageInflowMask(GenericMask):
    """Operational positions with nonzero exogenous storage inflow."""

    name = "storage_inflow"

    @classmethod
    def build(cls, model_constructor, registry):
        model = model_constructor.optimization_model
        technologies = list(model.sets["set_storage_technologies"])
        if not technologies:
            return xr.DataArray(
                False,
                coords={
                    "set_technologies": technologies,
                    "set_location": list(model.sets["set_nodes"]),
                    "set_years": list(model.sets["set_years"]),
                    "set_representative_hours": list(
                        model.sets["set_representative_hours"]
                    ),
                },
                dims=(
                    "set_technologies",
                    "set_location",
                    "set_years",
                    "set_representative_hours",
                ),
            )
        inflow = model.parameters.flow_storage_inflow
        return (inflow.fillna(0) != 0).rename(
            {
                "set_storage_technologies": "set_technologies",
                "set_nodes": "set_location",
            }
        )
