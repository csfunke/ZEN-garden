from zen_garden.model.component_types.constraint import GenericConstraint


class CostCarrierTotalConstraint(GenericConstraint):
    @classmethod
    def build(cls, model_constructor):
        """Summary:
        Total cost of importing and exporting carrier.

        Formulation:

        .. math::
            C^{\\mathrm{carrier}}_y = \\sum_{c\\in\\mathcal{C}}\\sum_{n\\in\\mathcal{N}}
            \\sum_{t\\in\\mathcal{T}_y} \\Delta t_t (C^{\\mathrm{carrier}}_{c,n,t}
            + C^{\\mathrm{shed}}_{c,n,t})

        Notation:

        :math:`C^{\\mathrm{carrier}}_{c,n,t}`: cost of importing and exporting carrier
        :math:`c` at node :math:`n` in time step :math:`t` of year :math:`y`
        :math:`C^{\\mathrm{shed}}_{c,n,t}`: cost of shedding
        demand of carrier :math:`c` at node :math:`n` in time step :math:`t` of year
        :math:`y`
        :math:`\\Delta t_t`: duration of time step :math:`t`
        """
        weight = (
            model_constructor.optimization_model.parameters.weight_representative_hours
        )
        term_summed_cost_carrier = (
            (
                model_constructor.optimization_model.variables["cost_carrier"]
                + model_constructor.optimization_model.variables["cost_shed_demand"]
            )
            * weight
        ).sum(["set_carriers", "set_nodes", "set_representative_hours"])
        lhs = (
            model_constructor.optimization_model.variables["cost_carrier_total"]
            - term_summed_cost_carrier
        )
        rhs = 0
        constraints = lhs == rhs

        model_constructor.optimization_model.add_constraint(
            "constraint_cost_carrier_total", constraints
        )
