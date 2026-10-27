from zen_garden.model.component_types.constraint import GenericConstraint


class RetrofitFlowCouplingConstraint(GenericConstraint):
    """Limit retrofit activity by the activity of its base technology."""

    name = "constraint_retrofit_flow_coupling"
    indices = (
        "set_conversion_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        coupling = model.parameters.retrofit_flow_coupling_factor.rename(
            {"set_retrofitting_technologies": "set_conversion_technologies"}
        )
        return model.expressions["retrofit_base_activity"] <= (
            coupling * model.expressions["retrofit_activity"]
        )
