import itertools

import pandas as pd
import xarray as xr

from zen_garden.elements.technology.diffusion import (
    diffusion_rate,
    technology_type_mask,
)
from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromSpillovers(GenericExpression):
    """Capacity growth supported by local and cross-location installation knowledge."""

    name = "capacity_growth_from_spillovers"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )

    @classmethod
    def should_construct(cls, model_constructor):
        return (
            model_constructor.optimization_model.parameters.knowledge_spillover_rate
            != float("inf")
        )

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct the model component.

        Summary:
            Capacity growth supported by local and cross-location installation
            knowledge.

        Formulation:

        .. math::

            d_{h,p,y} \\sum_{v<y}[ \\Delta K_{h,q,p,v} +s_h \\sum_{p\\prime\\ne p}
            \\Delta K_{h,q,p\\prime,v}](1-\\delta_h)^{ \\Delta y(y-1-v)}

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Expression over its declared model indices.
        """
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
                (year, previous): (1 - depreciation)
                ** (interval * (year - 1 - previous))
                for year, previous in years
            }
        )
        factors_series.index.names = ["set_years", "set_years_prev"]
        previous_years = pd.Series(index=years, data=1).to_xarray().fillna(0)
        additions = capacity_addition.rename(
            {"set_years": "set_years_prev"}
        ).broadcast_like(previous_years)
        factors = factors_series.to_xarray().fillna(0).broadcast_like(additions.lower)
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
