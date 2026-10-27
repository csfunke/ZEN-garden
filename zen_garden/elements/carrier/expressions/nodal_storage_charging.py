"""Nodal carrier consumption from storage charging."""

from zen_garden.elements.carrier.nodal_flow import build_nodal_storage_flow
from zen_garden.model.component_types.expression import GenericExpression


class NodalStorageCharging(GenericExpression):
    """Aggregate charging flow by storage reference carrier and node."""

    name = "nodal_storage_charging"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    units = "energy per time"

    @classmethod
    def get_expression(cls, model_constructor):
        return build_nodal_storage_flow(model_constructor, "charge")
