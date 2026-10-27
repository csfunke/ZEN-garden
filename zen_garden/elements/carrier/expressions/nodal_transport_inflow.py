"""Net transport inflow by carrier and node."""

from zen_garden.elements.carrier.nodal_flow import build_nodal_transport_flow
from zen_garden.model.component_types.expression import GenericExpression


class NodalTransportInflow(GenericExpression):
    """Aggregate incoming transport flow after losses."""

    name = "nodal_transport_inflow"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    units = "energy per time"

    @classmethod
    def get_expression(cls, model_constructor):
        return build_nodal_transport_flow(model_constructor, "in")
