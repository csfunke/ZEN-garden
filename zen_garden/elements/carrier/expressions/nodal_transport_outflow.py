"""Transport outflow by carrier and node."""

from zen_garden.elements.carrier.nodal_flow import build_nodal_transport_flow
from zen_garden.model.component_types.expression import GenericExpression


class NodalTransportOutflow(GenericExpression):
    """Aggregate outgoing transport flow."""

    name = "nodal_transport_outflow"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    units = "energy per time"

    @classmethod
    def get_expression(cls, model_constructor):
        return build_nodal_transport_flow(model_constructor, "out")
