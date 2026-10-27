"""Algebraic building blocks for technology diffusion expressions."""

import itertools

import pandas as pd
import xarray as xr


def _class_technologies(model_constructor, technology):
    """Return technologies belonging to the same concrete element class."""
    model = model_constructor.optimization_model
    element = model_constructor.element_registry.get_element_by_name(technology)
    if element is None:
        raise ValueError(f"Element {technology} not found")
    return model.sets[element.label]


def diffusion_rate(model_constructor):
    """Return maximum capacity growth over one investment interval."""
    model = model_constructor.optimization_model
    interval = model_constructor.config.system.interval_between_years
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


def previous_addition_growth(model_constructor, *, include_spillovers: bool):
    """Return diffusion growth supported by depreciated earlier additions."""
    model = model_constructor.optimization_model
    capacity_addition = model.variables["capacity_addition"]
    years = pd.MultiIndex.from_tuples(
        [
            (year, previous)
            for year, previous in itertools.product(
                model.sets["set_years"], model.sets["set_years"]
            )
            if previous < year
        ],
        names=["set_years", "set_years_prev"],
    )
    if not len(years):
        return capacity_addition.where(xr.DataArray(False))

    interval = model_constructor.config.system.interval_between_years
    depreciation = model.parameters.knowledge_depreciation_rate
    factors_series = pd.Series(
        {
            (year, previous): (1 - depreciation) ** (interval * (year - 1 - previous))
            for year, previous in years
        }
    )
    factors_series.index.names = ["set_years", "set_years_prev"]
    previous_years = pd.Series(index=years, data=1).to_xarray().fillna(0)
    additions = capacity_addition.rename(
        {"set_years": "set_years_prev"}
    ).broadcast_like(previous_years)
    factors = factors_series.to_xarray().fillna(0).broadcast_like(additions.lower)

    knowledge = additions
    if include_spillovers:
        location_index = pd.Series(
            index=pd.MultiIndex.from_product(
                [
                    capacity_addition.coords["set_location"].values,
                    capacity_addition.coords["set_location"].values,
                ],
                names=["set_location", "set_location_temp"],
            )
        ).to_xarray()
        additions_at_nodes = (
            additions.rename({"set_location": "set_location_temp"})
            .broadcast_like(location_index)
            .sel(set_location_temp=model.sets["set_nodes"])
            .sum("set_location_temp")
        )
        spillovers = additions_at_nodes - additions
        spillover_rate = xr.full_like(
            spillovers.const, model.parameters.knowledge_spillover_rate
        )
        type_mask = technology_type_mask(model_constructor)
        node_mask = pd.Series(
            index=pd.Index(capacity_addition.coords["set_location"]), data=1
        )
        node_mask.index.name = "set_location"
        node_mask[node_mask.index.isin(model.sets["set_edges"])] = 0
        knowledge = (
            additions
            + spillover_rate.where(type_mask, 0).where(node_mask.to_xarray(), 0)
            * spillovers
        )

    return diffusion_rate(model_constructor) * (knowledge * factors).sum(
        "set_years_prev"
    )


def unbounded_market_growth(model_constructor):
    """Return growth supported by other technologies serving the same carrier."""
    model = model_constructor.optimization_model
    capacity_previous = model.variables["capacity_previous"]

    shares = {
        (technology, other): (
            model.parameters.market_share_unbounded
            if other != technology
            and model.sets["set_reference_carriers"][technology][0]
            == model.sets["set_reference_carriers"][other][0]
            else 0
        )
        for technology in model.sets["set_technologies"]
        for other in _class_technologies(model_constructor, technology)
    }
    shares = pd.Series(shares)
    shares.index.names = ["set_technologies", "set_other_technologies"]
    shares = shares.to_xarray().broadcast_like(capacity_previous.lower).fillna(0)
    return (
        (
            shares
            * capacity_previous.rename({"set_technologies": "set_other_technologies"})
        )
        .where(shares != 0)
        .sum("set_other_technologies")
    )


def existing_capacity_growth(model_constructor, *, include_spillovers: bool):
    """Return growth supported by depreciated pre-horizon capacity."""
    model = model_constructor.optimization_model
    interval = model_constructor.config.system.interval_between_years
    capacity_addition = model.variables["capacity_addition"]
    capacity_existing = model.parameters.capacity_existing
    years_from_start = interval * (
        capacity_addition.coords["set_years"] - model.sets["set_years"][0]
    )
    lifetime_existing = model.parameters.lifetime_existing
    lifetime = model.parameters.lifetime
    depreciation = model.parameters.knowledge_depreciation_rate
    factor = (1 - depreciation) ** (years_from_start - 1 + lifetime - lifetime_existing)
    factor = factor.where(lifetime >= lifetime_existing - years_from_start, 0)
    if include_spillovers:
        spillover_rate = model.parameters.knowledge_spillover_rate
        capacity_existing = capacity_existing + spillover_rate * (
            capacity_existing.sum("set_location") - capacity_existing
        ).where(technology_type_mask(model_constructor), 0)
    return diffusion_rate(model_constructor) * (capacity_existing * factor).sum(
        "set_technologies_existing"
    )
