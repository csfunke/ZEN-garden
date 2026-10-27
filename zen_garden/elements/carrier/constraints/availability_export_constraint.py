from zen_garden.model.component_types.constraint import GenericConstraint


class AvailabilityExportConstraint(GenericConstraint):
    """Limit hourly exports to their node- and time-specific availability."""

    name = "constraint_availability_export"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        return model.variables["flow_export"] <= model.parameters.availability_export
