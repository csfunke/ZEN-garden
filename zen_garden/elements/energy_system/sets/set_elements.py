from zen_garden.model.component_types.set import GenericSet


class SetElements(GenericSet):
    name = "set_elements"
    symbol = r"a \in \mathcal{A}"
    doc = "Set of elements."
    indexing_set = True

    @classmethod
    def get_data(cls, model_constructor):
        return list(
            set(model_constructor.model_schema.set_technologies)
            | set(model_constructor.model_schema.set_carriers)
        )
