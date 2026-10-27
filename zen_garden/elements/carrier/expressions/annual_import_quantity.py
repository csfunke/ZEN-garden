"""Annual imported carrier quantity."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualImportQuantity(GenericExpression):
    """Weight and sum imported flow over representative hours."""

    name = "annual_import_quantity"
    indices = ("set_carriers", "set_nodes", "set_years")
    units = "energy"

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            optimization_model.variables["flow_import"]
            * optimization_model.parameters.weight_representative_hours
        ).sum("set_representative_hours")
