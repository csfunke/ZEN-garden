"""Dependent-carrier flow of conversion technologies."""

import itertools

import linopy as lp
import pandas as pd
from linopy.expressions import LinearExpression

from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.utils import align_like


class ConversionDependentFlow(GenericExpression):
    """Select all configured dependent-carrier conversion flows."""

    name = "conversion_dependent_flow"
    indices = (
        "set_conversion_technologies",
        "set_dependent_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @staticmethod
    def _dependent_carrier_mask(technologies, carriers, dependent_carriers):
        """Return configured dependent-carrier membership by technology."""
        mask = pd.Series(
            {
                (technology, carrier): carrier in dependent_carriers[technology]
                for technology, carrier in itertools.product(technologies, carriers)
            }
        )
        mask.index.names = [
            "set_conversion_technologies",
            "set_dependent_carriers",
        ]
        return mask

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct select all configured dependent-carrier conversion flows.

        Summary:
            Select all configured dependent-carrier conversion flows.

        Formulation:

        .. math::

            \\{F^{in}_{h,c,n,y,r}:c \\in \\mathcal C_h^{dep} \\cap \\mathcal C_h^{in}\\}
            \\cup\\{F^{out}_{h,c,n,y,r}:c \\in \\mathcal C_h^{dep} \\cap \\mathcal
            C_h^{out}\\}

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
        input_flow = optimization_model.variables["flow_conversion_input"].rename(
            {"set_input_carriers": "set_dependent_carriers"}
        )
        output_flow = optimization_model.variables["flow_conversion_output"].rename(
            {"set_output_carriers": "set_dependent_carriers"}
        )
        technologies = optimization_model.sets["set_conversion_technologies"]

        input_mask = align_like(
            cls._dependent_carrier_mask(
                technologies,
                optimization_model.sets["set_input_carriers"].coordinate_values,
                optimization_model.sets["set_dependent_carriers"],
            ).to_xarray(),
            input_flow,
            astype=bool,
        )
        output_mask = align_like(
            cls._dependent_carrier_mask(
                technologies,
                optimization_model.sets["set_output_carriers"].coordinate_values,
                optimization_model.sets["set_dependent_carriers"],
            ).to_xarray(),
            output_flow,
            astype=bool,
        )
        return lp.merge(
            [1 * input_flow.where(input_mask), 1 * output_flow.where(output_mask)],
            compat="broadcast_equals",
            join="outer",
            cls=LinearExpression,
        )
