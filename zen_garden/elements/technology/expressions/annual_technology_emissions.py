"""Annual operating emissions from technologies."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualTechnologyEmissions(GenericExpression):
    """Aggregate technology emissions over technologies, locations, and hours."""

    name = "annual_technology_emissions"
    indices = ("set_years",)
    units = "mass of carbon dioxide equivalent per year"

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            optimization_model.variables["carbon_emissions_technology"]
            * optimization_model.parameters.weight_representative_hours
        ).sum(["set_technologies", "set_location", "set_representative_hours"])
