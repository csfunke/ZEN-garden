from zen_garden.model.component_types.constraint import GenericConstraint
from zen_garden.model.linear_expression import align_and_mask


class TechnologyOnOffCapacityHelperUpperBoundConstraint(GenericConstraint):
    """Apply the upper capacity bound to the on/off capacity helper."""

    name = "constraint_technology_on_off_capacity_helper_upper_bound"
    indices = (
        "set_technologies",
        "set_location",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def should_construct(cls, model_constructor):
        technologies = model_constructor.optimization_model.create_custom_set(
            ["set_technologies", "set_on_off"]
        )[0]
        return bool(technologies)

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        helper = model.variables["capacity_on_off_helper_var"]
        capacity = model.variables["capacity"].sel(set_capacity_types="power")
        return align_and_mask(helper - capacity, helper.mask) <= 0
