"""Annual exported carrier quantity."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualExportQuantity(GenericExpression):
    """Weight and sum exported flow over representative hours."""

    name = "annual_export_quantity"
    indices = ("set_carriers", "set_nodes", "set_years")

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            optimization_model.variables["flow_export"]
            * optimization_model.parameters.weight_representative_hours
        ).sum("set_representative_hours")
