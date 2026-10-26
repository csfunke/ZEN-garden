from zen_garden.model.component_types.parameter import GenericParameter


class WeightRepresentativeHours(GenericParameter):
    """Amount of original time represented by each operational hour."""

    name = "weight_representative_hours"
    indices = ("set_years", "set_representative_hours")
    doc = "Weight of each operational representative hour"
    unit_category = {"time": 1}
    squeeze_singleton = False

    @classmethod
    def store_input_data(cls, element):
        """Retain weights populated by time-series aggregation."""
