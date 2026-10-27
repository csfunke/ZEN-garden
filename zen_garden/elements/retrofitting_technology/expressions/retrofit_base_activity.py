"""Operational activity of technologies that can be retrofitted."""

from zen_garden.model.component_types.expression import GenericExpression


class RetrofitBaseActivity(GenericExpression):
    """Select reference flow for technologies participating in retrofits."""

    name = "retrofit_base_activity"
    indices = (
        "set_conversion_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    dependencies = ("conversion_reference_flow",)

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct select reference flow for technologies participating in retrofits.

        Summary:
            Select reference flow for technologies participating in retrofits.

        Formulation:

        .. math::

            \\{F^{ref}_{b,n,y,r}:b\\in\\mathcal H^{base}\\}

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
        return optimization_model.expressions["conversion_reference_flow"].sel(
            {
                "set_conversion_technologies": optimization_model.sets[
                    "set_retrofitting_technologies"
                ]
            }
        )
