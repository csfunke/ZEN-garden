"""Change in cumulative emissions between modeled years."""

from zen_garden.model.component_types.expression import GenericExpression


class CumulativeEmissionsChange(GenericExpression):
    """Account for annual emissions between cumulative-emissions states."""

    name = "cumulative_emissions_change"
    indices = ("set_years",)
    units = "mass of carbon dioxide equivalent"

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        cumulative = optimization_model.variables["carbon_emissions_cumulative"]
        annual = optimization_model.variables["carbon_emissions_annual"]
        return (
            cumulative
            - cumulative.shift(set_years=1)
            - annual.shift(set_years=1)
            * (model_constructor.config.system.interval_between_years - 1)
            - annual
        )
