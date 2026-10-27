"""Emissions quantity evaluated against the carbon budget."""

from zen_garden.model.component_types.expression import GenericExpression


class EmissionsCountedTowardBudget(GenericExpression):
    """Combine cumulative, annual, and budget-overshoot emissions."""

    name = "emissions_counted_toward_budget"
    indices = ("set_years",)
    units = "mass of carbon dioxide equivalent"

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        not_last_year = [
            year != model_constructor.model_schema.set_years_entire_horizon[-1]
            for year in model_constructor.model_schema.set_years
        ]
        return (
            optimization_model.variables["carbon_emissions_cumulative"]
            - optimization_model.variables["carbon_emissions_budget_overshoot"]
            + optimization_model.variables["carbon_emissions_annual"].where(
                not_last_year
            )
            * (model_constructor.config.system.interval_between_years - 1)
        )
