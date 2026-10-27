"""Transport capacity proposed on unavailable edges."""

import numpy as np

from zen_garden.model.component_types.expression import GenericExpression


class TransportCapacityOnUnavailableEdges(GenericExpression):
    """Select transport additions whose configured distance is infinite."""

    name = "transport_capacity_on_unavailable_edges"
    indices = ("set_technologies", "set_location", "set_years")

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
        unavailable = np.isinf(
            model.parameters.distance.rename(
                set_transport_technologies="set_technologies",
                set_edges="set_location",
            )
        )
        return addition.where(unavailable)
