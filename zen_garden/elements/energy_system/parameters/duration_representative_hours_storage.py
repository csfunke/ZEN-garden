from zen_garden.model.component_types.parameter import GenericParameter


class DurationRepresentativeHoursStorage(GenericParameter):
    """Duration of each storage representative hour."""

    name = "duration_representative_hours_storage"
    indices = ("set_years", "set_representative_hours_storage")
    doc = "Duration of each storage representative hour"
    unit_category = {"time": 1}
    squeeze_singleton = False

    @classmethod
    def store_input_data(cls, element):
        """Retain durations populated by time-series aggregation."""
