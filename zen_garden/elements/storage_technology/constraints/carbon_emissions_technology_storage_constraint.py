from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.model.component_types.constraint import GenericConstraint


class CarbonEmissionsTechnologyStorageConstraint(GenericConstraint):
    """Calculate operating emissions from storage throughput."""

    name = "constraint_carbon_emissions_technology_storage"
    indices = (
        "set_technologies",
        "set_location",
        "set_years",
        "set_representative_hours",
    )
    masks = (PowerOperationMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        """Construct calculate operating emissions from storage throughput.

        Summary:
            Calculate operating emissions from storage throughput.

        Formulation:

        .. math::

            E^{technology}=e^{technology}(F^{ch}+F^{dis})

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
        technologies = model.sets["set_storage_technologies"]
        nodes = model.sets["set_nodes"]
        emissions = model.variables["carbon_emissions_technology"].sel(
            set_technologies=technologies, set_location=nodes
        )
        return (
            emissions
            == model.parameters.carbon_intensity_technology
            * model.expressions["storage_throughput"]
        )
