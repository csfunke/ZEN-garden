import numpy as np

from zen_garden.elements.technology.masks import PowerCapacityAdditionMask
from zen_garden.model.component_types.constraint import GenericConstraint


class TransportTechnologyCapexConstraint(GenericConstraint):
    """Set transport CAPEX and prohibit additions on unavailable edges."""

    name = "constraint_transport_technology_capex"
    indices = ("set_technologies", "set_location", "set_years")
    masks = (PowerCapacityAdditionMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_transport_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        """Construct set transport capex and prohibit additions on unavailable edges.

        Summary:
            Set transport CAPEX and prohibit additions on unavailable edges.

        Formulation:

        .. math::

            C^{capex,overnight}=k^{capex,trans}\\Delta K+k^{distance}G

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        model = model_constructor.optimization_model
        technologies = model.sets["set_transport_technologies"]
        edges = model.sets["set_edges"]
        cost = model.variables["cost_capex_overnight"].sel(
            set_technologies=technologies,
            set_capacity_types="power",
            set_location=edges,
        )
        available = ~np.isinf(
            model.parameters.distance.rename(
                set_transport_technologies="set_technologies",
                set_edges="set_location",
            )
        )
        return (
            cost.where(available)
            - model.expressions["transport_overnight_capex"]
            + model.expressions["transport_capacity_on_unavailable_edges"]
            == 0
        )
