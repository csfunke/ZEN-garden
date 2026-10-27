from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.elements.transport_technology.masks import FiniteTransportRouteMask
from zen_garden.model.component_types.constraint import GenericConstraint


class OpexTechnologyTransportConstraint(GenericConstraint):
    """Calculate variable OPEX from transported flow."""

    name = "constraint_opex_technology_transport"
    indices = (
        "set_transport_technologies",
        "set_edges",
        "set_years",
        "set_representative_hours",
    )
    masks = (PowerOperationMask, FiniteTransportRouteMask)

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_transport_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        technologies = model.sets["set_transport_technologies"]
        edges = model.sets["set_edges"]
        cost = (
            model.variables["cost_opex_variable"]
            .sel(set_technologies=technologies, set_location=edges)
            .rename(
                set_technologies="set_transport_technologies", set_location="set_edges"
            )
        )
        factor = model.parameters.opex_specific_variable.sel(
            set_technologies=technologies, set_location=edges
        ).rename(
            set_technologies="set_transport_technologies", set_location="set_edges"
        )
        return cost == factor * model.variables["flow_transport"]
