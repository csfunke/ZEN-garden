from zen_garden.model.component_types.constraint import GenericConstraint
from zen_garden.model.linear_expression import align_and_mask


class TechnologyOnOffOperationUpperBoundConstraint(GenericConstraint):
    """Limit technology activity to capacity while switched on."""

    name = "constraint_technology_on_off_operation_upper_bound"
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
        """Construct limit technology activity to capacity while switched on.

        Summary:
            Limit technology activity to capacity while switched on.

        Formulation:

        .. math::

            A\\leq H

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        model = model_constructor.optimization_model
        helper = model.variables["capacity_on_off_helper_var"]
        activity = model.expressions["technology_activity"].reindex_like(helper.mask)
        return align_and_mask(activity - helper, helper.mask) <= 0
