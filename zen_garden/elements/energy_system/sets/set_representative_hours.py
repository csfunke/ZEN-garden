from zen_garden.model.component_types.set import GenericSet


class SetRepresentativeHours(GenericSet):
    """Operational representative hours shared by every modeled year."""

    name = "set_representative_hours"
    doc = "Set of operational representative hours"

    @classmethod
    def get_data(cls, model_constructor):
        representative_hours = model_constructor.time_steps.representative_hours
        assert representative_hours is not None
        return representative_hours
