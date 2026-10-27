"""Unified operational activity for all technology types."""

import linopy as lp
from linopy.expressions import LinearExpression

from zen_garden.model.component_types.expression import GenericExpression


class TechnologyActivity(GenericExpression):
    """Combine conversion, storage, and transport operational activity."""

    name = "technology_activity"
    indices = (
        "set_technologies",
        "set_location",
        "set_years",
        "set_representative_hours",
    )
    dependencies = ("conversion_reference_flow", "storage_throughput")

    @classmethod
    def should_construct(cls, model_constructor):
        technologies = model_constructor.optimization_model.create_custom_set(
            ["set_technologies", "set_on_off"]
        )[0]
        return bool(technologies)

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct combine conversion, storage, and transport operational activity.

        Summary:
            Combine conversion, storage, and transport operational activity.

        Formulation:

        .. math::

            \\begin{cases}F^{ref}_{h,p,y,r}&h \\in \\mathcal
            H^{conv}\\\\F^{trans}_{h,p,y,r}&h \\in \\mathcal
            H^{trans}\\\\F^{ch}_{h,p,y,r} +F^{dis}_{h,p,y,r}&h \\in \\mathcal
            H^{storage}\\end{cases}

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
        conversion = optimization_model.expressions["conversion_reference_flow"].rename(
            {
                "set_conversion_technologies": "set_technologies",
                "set_nodes": "set_location",
            }
        )
        transport = optimization_model.variables["flow_transport"].rename(
            {
                "set_transport_technologies": "set_technologies",
                "set_edges": "set_location",
            }
        )
        activities = [conversion, 1 * transport]
        if "storage_throughput" in optimization_model.expressions:
            activities.append(optimization_model.expressions["storage_throughput"])
        return lp.merge(
            activities,
            compat="broadcast_equals",
            join="outer",
            cls=LinearExpression,
        )
