from zen_garden.model.component_types.parameter import GenericParameter


class IntervalBetweenYears(GenericParameter):
    """Number of calendar years represented by one planning period."""

    name = "interval_between_years"
    symbol = r"\Delta y"
    indices = ()
    doc = "Number of calendar years represented by one planning period."
    unit_category = {"time": 1}

    @classmethod
    def get_model_data(cls, model_constructor, index_names):
        """Return the configured interval as a scalar parameter."""
        return model_constructor.config.system.interval_between_years, index_names, {}

    @classmethod
    def store_input_data(cls, element):
        """Skip element input because this value comes from system configuration."""
