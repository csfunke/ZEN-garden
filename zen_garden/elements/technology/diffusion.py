"""Shared technology-diffusion calculations."""

import pandas as pd


def diffusion_rate(model_constructor):
    """Return maximum capacity growth over one investment interval."""
    model = model_constructor.optimization_model
    interval = model_constructor.optimization_model.parameters.interval_between_years
    rate = (1 + model.parameters.max_diffusion_rate) ** interval - 1
    return rate.broadcast_like(model.variables["capacity_addition"].lower)


def technology_type_mask(model_constructor):
    """Return one for conversion/storage technologies and zero for transport."""
    model = model_constructor.optimization_model
    mask = pd.Series(index=pd.Index(model.sets["set_technologies"]), data=1)
    mask.index.name = "set_technologies"
    mask[mask.index.isin(model.sets["set_transport_technologies"])] = 0
    return mask.to_xarray()


def technology_location_mask(model_constructor):
    """Select valid node technologies and valid edge transport technologies."""
    model = model_constructor.optimization_model
    capacity_addition = model.variables["capacity_addition"]
    type_mask = technology_type_mask(model_constructor)
    location_mask = pd.Series(
        index=pd.Index(capacity_addition.coords["set_location"]), data=1
    )
    location_mask.index.name = "set_location"
    location_mask[location_mask.index.isin(model.sets["set_edges"])] = 0
    location_mask = location_mask.to_xarray()
    return ((1 - type_mask) & (1 - location_mask)) | (type_mask & location_mask)
