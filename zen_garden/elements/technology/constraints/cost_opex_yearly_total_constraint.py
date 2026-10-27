from zen_garden.model.component_types.constraint import GenericConstraint


class CostOpexYearlyTotalConstraint(GenericConstraint):
    name = "constraint_cost_opex_yearly_total"
    indices = ("set_years",)

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Sums over all technologies to calculate total opex.

        Formulation:

        .. math::
            C^{\\mathrm{op}}_y = \\sum_{h\\in\\mathcal{H}}
            \\sum_{p\\in\\mathcal{P}_h} C^{\\mathrm{op,ann}}_{h,p,y}

        Notation:

        :math:`C^{\\mathrm{op,ann}}_{h,p,y}`: OPEX of operating technology :math:`h` at
        location :math:`p` in year :math:`y`
        """
        lhs = model_constructor.optimization_model.variables[
            "cost_opex_yearly_total"
        ] - model_constructor.optimization_model.variables["cost_opex_yearly"].sum(
            ["set_technologies", "set_location"]
        )
        rhs = 0
        constraints = lhs == rhs

        return constraints
