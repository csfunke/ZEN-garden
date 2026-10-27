"""Operational activity of retrofit technologies."""

import pandas as pd

from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.model.linear_expression import map_and_expand


class RetrofitActivity(GenericExpression):
    """Map reference flow to the configured retrofit technologies."""

    name = "retrofit_activity"
    indices = (
        "set_conversion_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    dependencies = ("conversion_reference_flow",)

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        mapping = pd.Series(
            {
                technology: retrofit
                for technology in optimization_model.sets["set_conversion_technologies"]
                if technology
                in optimization_model.sets["set_retrofitting_base_technologies"]
                for retrofit in optimization_model.sets[
                    "set_retrofitting_base_technologies"
                ][technology]
            },
            name="set_conversion_technologies",
        )
        mapping.index.name = "set_conversion_technologies"
        return map_and_expand(
            optimization_model.expressions["conversion_reference_flow"], mapping
        )
