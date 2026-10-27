from zen_garden.model.component_types.expression import GenericExpression


class TotalCost(GenericExpression):
    """Total net present cost objective expression.

    .. math::
        J = \\sum_{y\\in\\mathcal{Y}} NPC_y
    """

    name = "total_cost"
    indices = ()
    doc = "Total net present cost, summed over all modeled years"

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct total net present cost objective expression.

        Summary:
            Total net present cost objective expression.

        Formulation:

        .. math::

            \\sum_yC^{NPC}_y

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Expression over its declared model indices.
        """
        return model_constructor.optimization_model.variables["net_present_cost"].sum(
            "set_years"
        )
