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
    units = "energy per time"
    dependencies = ("conversion_reference_flow",)

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        return optimization_model.expressions["conversion_reference_flow"].sel(
            {
                "set_conversion_technologies": optimization_model.sets[
                    "set_retrofitting_technologies"
                ]
            }
        )
