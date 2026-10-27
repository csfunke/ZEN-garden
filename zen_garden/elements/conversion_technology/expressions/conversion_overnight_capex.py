"""Overnight CAPEX of conversion-capacity additions."""

import numpy as np

from zen_garden.model.component_types.expression import GenericExpression


class ConversionOvernightCapex(GenericExpression):
    """Multiply conversion power additions by their specific CAPEX."""

    name = "conversion_overnight_capex"
    indices = ("set_technologies", "set_location", "set_years")

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct multiply conversion power additions by their specific capex.

        Summary:
            Multiply conversion power additions by their specific CAPEX.

        Formulation:

        .. math::

            k^{capex,conv}_{h,n,y}\\Delta K_{h,power,n,y}

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Expression over its declared model indices.
        """
        model = model_constructor.optimization_model
        technologies = model.sets["set_conversion_technologies"]
        nodes = model.sets["set_nodes"]
        addition = model.variables["capacity_addition"].sel(
            set_technologies=technologies,
            set_capacity_types="power",
            set_location=nodes,
        )
        specific = model.parameters.capex_specific_conversion.rename(
            {
                old: new
                for old, new in zip(
                    model.parameters.capex_specific_conversion.dims,
                    ["set_technologies", "set_location", "set_years"],
                    strict=False,
                )
            }
        ).broadcast_like(addition.lower)
        return (specific * addition).where(~np.isnan(specific))
