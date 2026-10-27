"""Reference-carrier flow of conversion technologies."""

import itertools

import pandas as pd

from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.utils import align_like


class ConversionReferenceFlow(GenericExpression):
    """Select each conversion technology's configured reference-carrier flow."""

    name = "conversion_reference_flow"
    indices = (
        "set_conversion_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        input_flow = optimization_model.variables["flow_conversion_input"]
        output_flow = optimization_model.variables["flow_conversion_output"]
        technologies = optimization_model.sets["set_conversion_technologies"]
        input_mask = pd.Series(
            {
                (technology, carrier): carrier
                in optimization_model.sets["set_reference_carriers"][technology]
                for technology, carrier in itertools.product(
                    technologies,
                    optimization_model.sets["set_input_carriers"].coordinate_values,
                )
            }
        )
        output_mask = pd.Series(
            {
                (technology, carrier): carrier
                in optimization_model.sets["set_reference_carriers"][technology]
                for technology, carrier in itertools.product(
                    technologies,
                    optimization_model.sets["set_output_carriers"].coordinate_values,
                )
            }
        )
        input_mask.index.names = [
            "set_conversion_technologies",
            "set_input_carriers",
        ]
        output_mask.index.names = [
            "set_conversion_technologies",
            "set_output_carriers",
        ]
        input_mask = align_like(input_mask.to_xarray(), input_flow, astype=bool)
        output_mask = align_like(output_mask.to_xarray(), output_flow, astype=bool)
        return input_flow.where(input_mask).sum(
            "set_input_carriers"
        ) + output_flow.where(output_mask).sum("set_output_carriers")
