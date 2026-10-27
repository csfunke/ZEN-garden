"""Annual cost of carrier trading and demand shedding."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualCarrierCost(GenericExpression):
    """Aggregate carrier and shedding costs over carriers, nodes, and hours."""

    name = "annual_carrier_cost"
    indices = ("set_years",)
    units = "currency per year"

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return (
            (
                optimization_model.variables["cost_carrier"]
                + optimization_model.variables["cost_shed_demand"]
            )
            * optimization_model.parameters.weight_representative_hours
        ).sum(["set_carriers", "set_nodes", "set_representative_hours"])
