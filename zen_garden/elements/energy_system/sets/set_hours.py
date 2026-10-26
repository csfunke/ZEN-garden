from zen_garden.model.component_types.set import GenericSet


class SetHours(GenericSet):
    """Unaggregated within-year input hours."""

    name, doc = "set_hours", "Set of unaggregated within-year hours"

    @classmethod
    def get_data(cls, model_constructor):
        return model_constructor.model_schema.set_hours
