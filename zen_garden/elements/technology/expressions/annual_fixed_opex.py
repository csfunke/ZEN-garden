"""Annual fixed operating expenditure."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualFixedOpex(GenericExpression):
    """Calculate fixed OPEX from installed power and energy capacity."""

    name = "annual_fixed_opex"
    indices = ("set_technologies", "set_location", "set_years")

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            optimization_model.parameters.opex_specific_fixed
            * optimization_model.variables["capacity"]
        ).sum("set_capacity_types")
