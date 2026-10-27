"""Net carrier supply at each model node."""

import linopy as lp
from linopy.expressions import LinearExpression

from zen_garden.model.component_types.expression import GenericExpression


class NodalNetSupply(GenericExpression):
    """Combine all production, consumption, trade, and storage flows."""

    name = "nodal_net_supply"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    dependencies = (
        "nodal_conversion_consumption",
        "nodal_conversion_production",
        "nodal_transport_inflow",
        "nodal_transport_outflow",
        "nodal_storage_charging",
        "nodal_storage_discharging",
    )

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct combine all production, consumption, trade, and storage flows.

        Summary:
            Combine all production, consumption, trade, and storage flows.

        Formulation:

        .. math::

             \\sum_{h:c \\in \\mathcal C_h^{out}}F^{out}_{h,c,n,y,r}- \\sum_{h:c \\in
            \\mathcal C_h^{in}}F^{in}_{h,c,n,y,r} + \\sum_{h,e
            \\in\\delta^-(n)}(F^{trans}_{h,e,y,r}-F^{loss}_{h,e,y,r})- \\sum_{h,e
            \\in\\delta^ +(n)}F^{trans}_{h,e,y,r}- \\sum_{h:c_h^{ref}
            =c}F^{ch}_{h,n,y,r} + \\sum_{h:c_h^{ref} =c}F^{dis}_{h,n,y,r}
            +F^{imp}_{c,n,y,r}-F^{exp}_{c,n,y,r} +F^{shed}_{c,n,y,r}

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
        expressions = optimization_model.expressions
        return lp.merge(
            [
                expressions["nodal_conversion_production"],
                -expressions["nodal_conversion_consumption"],
                expressions["nodal_transport_inflow"],
                -expressions["nodal_transport_outflow"],
                -expressions["nodal_storage_charging"],
                expressions["nodal_storage_discharging"],
                1 * optimization_model.variables["flow_import"],
                -optimization_model.variables["flow_export"],
                1 * optimization_model.variables["shed_demand"],
            ],
            compat="broadcast_equals",
            join="outer",
            cls=LinearExpression,
        )
