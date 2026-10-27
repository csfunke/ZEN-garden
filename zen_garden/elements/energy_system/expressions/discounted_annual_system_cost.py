"""Discounted annual system cost."""

import pandas as pd

from zen_garden.model.component_types.expression import GenericExpression


class DiscountedAnnualSystemCost(GenericExpression):
    """Apply intra-period economic discounting to annual system cost."""

    name = "discounted_annual_system_cost"
    indices = ("set_years",)

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        years = model_constructor.model_schema.set_years
        factor = pd.Series(index=years, dtype=float)
        for year in years:
            interval = (
                1
                if year == model_constructor.model_schema.set_years_entire_horizon[-1]
                else model_constructor.config.system.interval_between_years
            )
            factor[year] = sum(
                (1 / (1 + optimization_model.parameters.discount_rate))
                ** (
                    model_constructor.config.system.interval_between_years
                    * (year - years[0])
                    + intermediate_step
                )
                for intermediate_step in range(interval)
            )
        return optimization_model.variables["cost_total"] * factor
