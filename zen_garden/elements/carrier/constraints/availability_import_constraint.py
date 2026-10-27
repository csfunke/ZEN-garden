from zen_garden.model.component_types.constraint import GenericConstraint


class AvailabilityImportConstraint(GenericConstraint):
    """Limit hourly imports to their node- and time-specific availability."""

    name = "constraint_availability_import"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        return model.variables["flow_import"] <= model.parameters.availability_import
