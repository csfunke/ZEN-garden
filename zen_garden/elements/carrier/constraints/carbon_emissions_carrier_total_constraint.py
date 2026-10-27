from zen_garden.model.component_types.constraint import GenericConstraint


class CarbonEmissionsCarrierTotalConstraint(GenericConstraint):
    name = "constraint_carbon_emissions_carrier_total"
    indices = ("set_years",)

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Total carbon emissions of importing and exporting carrier.

        Formulation:

        .. math::
            M_y^{\\mathrm{carrier}} = \\sum_{c\\in\\mathcal{C}}\\sum_{n\\in\\mathcal{N}}
            \\sum_{t\\in\\mathcal{T}_y} \\Delta t_t
            M^{\\mathrm{carrier}}_{c,n,t}

        Notation:

        :math:`M^{\\mathrm{carrier}}_{c,n,t}`: carbon emissions of importing
        and exporting carrier :math:`c` at node :math:`n` in time step :math:`t`
        of year :math:`y`
        :math:`\\Delta t_t`: duration of time step :math:`t`
        """
        model = model_constructor.optimization_model
        return (
            model.variables["carbon_emissions_carrier_total"]
            == model.expressions["annual_import_export_emissions"]
        )
