from zen_garden.model.component_types.parameter import GenericParameter


class ModeledYearHours(GenericParameter):
    """Number of operational hours represented by a modeled year."""

    name = "modeled_year_hours"
    symbol = r"T^{\mathrm{model}}"
    indices = ()
    doc = "Number of operational hours represented by a modeled year."
    unit_category = {"time": 1}

    @classmethod
    def get_model_data(cls, model_constructor, index_names):
        """Return the configured modeled-year duration as a scalar parameter."""
        value = model_constructor.config.system.unaggregated_time_steps_per_year
        return value, index_names, {}

    @classmethod
    def store_input_data(cls, element):
        """Skip element input because this value comes from system configuration."""
