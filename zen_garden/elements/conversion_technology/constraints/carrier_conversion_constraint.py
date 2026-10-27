import linopy as lp
from linopy.expressions import LinearExpression

from zen_garden.model.component_types.constraint import GenericConstraint
from zen_garden.utils import align_like


class CarrierConversionConstraint(GenericConstraint):
    """Couple dependent-carrier flows to conversion reference flow."""

    name = "constraint_carrier_conversion"
    indices = (
        "set_conversion_technologies",
        "set_dependent_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        dependent_flow = model.expressions["conversion_dependent_flow"]
        conversion_factor = align_like(
            model.parameters.conversion_factor, dependent_flow
        )
        reference_flow = model.expressions["conversion_reference_flow"].broadcast_like(
            conversion_factor
        )
        converted_reference_flow = -conversion_factor * reference_flow
        converted_reference_flow = LinearExpression(
            converted_reference_flow.data.assign(
                const=converted_reference_flow.const.sum("_term")
            ),
            model.lp_model,
        )
        lhs = lp.merge(
            [dependent_flow, converted_reference_flow],
            compat="broadcast_equals",
            join="outer",
            cls=LinearExpression,
        )
        return lhs == 0
