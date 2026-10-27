from zen_garden.elements.technology.masks import CapacityAdditionEligibleMask
from zen_garden.model.component_types.constraint import GenericConstraint


class TechnologyMinCapacityAdditionConstraint(GenericConstraint):
    name = "constraint_technology_min_capacity_addition"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    masks = (CapacityAdditionEligibleMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        minimum = model_constructor.optimization_model.parameters.capacity_addition_min
        return bool(((minimum != 0) & minimum.notnull()).any().item())

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Min capacity addition of technology.

        Formulation:

        .. math::
            \\underline{\\Delta k}_{h} g_{h,p,y}
            \\leq \\Delta K_{h,p,y}

        The constraint is omitted for zero or missing minimum additions.

        Notation:

        :math:`\\underline{\\Delta k}_{h}`: minimum capacity addition for technology
        :math:`h` (with capacity type implicit)
        :math:`g_{h,p,y}`: binary variable which equals 1 if technology is installed
        at location :math:`p` in year :math:`y`
        :math:`\\Delta K_{h,p,y}`: capacity addition
        """
        capacity_addition_min = (
            model_constructor.optimization_model.parameters.capacity_addition_min
        )
        mask = (capacity_addition_min != 0) & (capacity_addition_min.notnull())

        lhs = mask * (
            capacity_addition_min
            * model_constructor.optimization_model.variables["technology_installation"]
            - model_constructor.optimization_model.variables["capacity_addition"]
        )
        rhs = 0
        constraints = lhs <= rhs

        ### return
        return constraints
