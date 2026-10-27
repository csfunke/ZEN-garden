from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.elements.transport_technology.masks import FiniteTransportRouteMask
from zen_garden.model.component_types.constraint import GenericConstraint


class CapacityFactorTransportConstraint(GenericConstraint):
    name = "constraint_capacity_factor_transport"
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
        """Summary:
        Load is limited by the installed capacity and the maximum load factor.

        Formulation:

        .. math::
            F^{\\mathrm{trans}}_{h,e,t} \\leq \\ell^{\\mathrm{max}}_{h,e,t}K_{h,e,y}

        Notation:

        :math:`F^{\\mathrm{trans}}_{h,e,t}`: carrier flow through transport
        technology :math:`h`
        on edge :math:`e` in time step :math:`t` of year :math:`y`
        :math:`\\ell^{\\mathrm{max}}_{h,e,t}`: Maximum load factor of transport
        technology :math:`h` on edge :math:`e` in time step :math:`t` of year
        :math:`y`
        :math:`K_{h,e,y}`: Capacity of transport technology :math:`h` on
        edge :math:`e` in year :math:`y`
        """
        techs = model_constructor.optimization_model.sets["set_transport_technologies"]
        edges = model_constructor.optimization_model.sets["set_edges"]
        term_capacity = (
            model_constructor.optimization_model.parameters.max_load.loc[
                techs, edges, :, :
            ]
            * model_constructor.optimization_model.variables["capacity"].loc[
                techs, "power", edges, :
            ]
        ).rename(
            {
                "set_technologies": "set_transport_technologies",
                "set_location": "set_edges",
            }
        )

        lhs = (
            term_capacity
            - model_constructor.optimization_model.variables["flow_transport"].loc[
                techs, edges, :, :
            ]
        )
        rhs = 0
        constraints = lhs >= rhs
        ### return
        return constraints
