"""Annual cost of carrier trading and demand shedding."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualCarrierCost(GenericExpression):
    """Aggregate carrier and shedding costs over carriers, nodes, and hours."""

    name = "annual_carrier_cost"
    indices = ("set_years",)

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct the model component.

        Summary:
            Aggregate carrier and shedding costs over carriers, nodes, and hours.

        Formulation:

        .. math::

            \\sum_{c,n,r} w_r(C^{carrier}_{c,n,y,r}+C^{shed}_{c,n,y,r})

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Expression over its declared model indices.
        """
        optimization_model = model_constructor.optimization_model
        return (
            (
                optimization_model.variables["cost_carrier"]
                + optimization_model.variables["cost_shed_demand"]
            )
            * optimization_model.parameters.weight_representative_hours
        ).sum(["set_carriers", "set_nodes", "set_representative_hours"])
