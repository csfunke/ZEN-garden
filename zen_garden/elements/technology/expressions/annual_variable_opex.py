"""Annual variable operating expenditure."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualVariableOpex(GenericExpression):
    """Weight and sum variable OPEX over representative hours."""

    name = "annual_variable_opex"
    indices = ("set_technologies", "set_location", "set_years")
    units = "currency per year"

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            optimization_model.variables["cost_opex_variable"]
            * optimization_model.parameters.weight_representative_hours
        ).sum("set_representative_hours")
