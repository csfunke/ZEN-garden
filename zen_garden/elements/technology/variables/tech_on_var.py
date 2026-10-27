from zen_garden.elements.technology.masks import (
    OnOffTechnologyMask,
    PowerOperationMask,
)
from zen_garden.model.component_types.variable import GenericVariable


class TechOnVar(GenericVariable):
    """Variable for technology on/off binary."""

    name = "tech_on_var"
    symbol = r"z^{\mathrm{on}}_{h,p,t}"
    indices = [
        "set_technologies",
        "set_location",
        "set_years",
        "set_representative_hours",
    ]
    doc = (
        "Binary variable which equals 1 when technology h is switched on at "
        "location p and operational time step t, else 0."
    )
    unit_category = {}
    binary = True
    masks = [PowerOperationMask, OnOffTechnologyMask]

    @classmethod
    def get_bounds(cls, model_constructor, index_sets):
        return None

    @classmethod
    def should_construct(cls, model_constructor):
        technologies = model_constructor.optimization_model.create_custom_set(
            ["set_technologies", "set_on_off"]
        )[0]
        return len(technologies) > 0
