import itertools

import pandas as pd
import xarray as xr

from zen_garden.elements.technology.diffusion import diffusion_rate
from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromLocalLearning(GenericExpression):
    """Capacity growth supported by depreciated additions at the same location."""

    name = "capacity_growth_from_local_learning"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )

    @classmethod
    def get_expression(cls, model_constructor):
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
        return diffusion_rate(model_constructor) * (additions * factors).sum(
            "set_years_prev"
        )
