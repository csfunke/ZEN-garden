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
