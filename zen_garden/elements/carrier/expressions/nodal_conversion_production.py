"""Nodal carrier production by conversion technologies."""

from zen_garden.elements.carrier.nodal_flow import build_nodal_conversion_flow
from zen_garden.model.component_types.expression import GenericExpression


class NodalConversionProduction(GenericExpression):
    """Aggregate conversion output flow by carrier and node."""

    name = "nodal_conversion_production"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    units = "energy per time"

    @classmethod
    def get_expression(cls, model_constructor):
        return build_nodal_conversion_flow(model_constructor, "output")
