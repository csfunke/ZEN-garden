"""Annual emissions associated with carrier imports and exports."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualImportExportEmissions(GenericExpression):
    """Aggregate carrier-trading emissions over carriers, nodes, and hours."""

    name = "annual_import_export_emissions"
    indices = ("set_years",)

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            optimization_model.variables["carbon_emissions_carrier"]
            * optimization_model.parameters.weight_representative_hours
        ).sum(["set_carriers", "set_nodes", "set_representative_hours"])
