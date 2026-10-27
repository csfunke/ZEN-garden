"""Overnight CAPEX of transport-capacity additions."""

import numpy as np

from zen_garden.model.component_types.expression import GenericExpression


class TransportOvernightCapex(GenericExpression):
    """Combine fixed and distance-dependent transport investment costs."""

    name = "transport_overnight_capex"
    indices = ("set_technologies", "set_location", "set_years")
    units = "currency"

    @classmethod
    def should_construct(cls, model_constructor):
        """Return whether transport technologies exist in the model."""
        return bool(
            model_constructor.optimization_model.sets["set_transport_technologies"]
        )

    @classmethod
    def get_expression(cls, model_constructor):
        model = model_constructor.optimization_model
        technologies = model.sets["set_transport_technologies"]
        edges = model.sets["set_edges"]
        addition = model.variables["capacity_addition"].sel(
            set_technologies=technologies,
            set_capacity_types="power",
            set_location=edges,
        )
        installation = model.variables["technology_installation"].sel(
            set_technologies=technologies,
            set_capacity_types="power",
            set_location=edges,
        )
        fixed = model.parameters.capex_specific_transport.rename(
            set_transport_technologies="set_technologies", set_edges="set_location"
        )
        distance_cost = model.parameters.transport_capex_distance.rename(
            set_transport_technologies="set_technologies", set_edges="set_location"
        )
        available = ~np.isinf(
            model.parameters.distance.rename(
                set_transport_technologies="set_technologies",
                set_edges="set_location",
            )
        )
        return (fixed * addition + distance_cost * installation).where(available)
