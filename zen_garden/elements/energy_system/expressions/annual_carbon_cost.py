"""Annual carbon-emissions cost."""

import numpy as np

from zen_garden.model.component_types.expression import GenericExpression


class AnnualCarbonCost(GenericExpression):
    """Combine emissions prices and configured overshoot penalties."""

    name = "annual_carbon_cost"
    indices = ("set_years",)

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        expression = (
            optimization_model.variables["carbon_emissions_annual"]
            * optimization_model.parameters.price_carbon_emissions
        )
        budget_price = (
            optimization_model.parameters.price_carbon_emissions_budget_overshoot
        )
        if budget_price != np.inf:
            last_year = [
                year == model_constructor.model_schema.set_years[-1]
                for year in model_constructor.model_schema.set_years
            ]
            expression += (
                optimization_model.variables["carbon_emissions_budget_overshoot"].where(
                    last_year
                )
                * budget_price.item()
            )
        annual_price = (
            optimization_model.parameters.price_carbon_emissions_annual_overshoot
        )
        if annual_price != np.inf:
            expression += (
                optimization_model.variables["carbon_emissions_annual_overshoot"]
                * annual_price.item()
            )
        return expression
