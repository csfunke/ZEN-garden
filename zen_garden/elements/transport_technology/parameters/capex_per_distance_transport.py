from zen_garden.model.component_types.parameter import GenericParameter


class CapexPerDistanceTransport(GenericParameter):
    """Capex per distance."""

    name = "capex_per_distance_transport"
    symbol = r"\kappa^{\mathrm{cap,dist}}_{h,e,y}"
    indices = ("set_transport_technologies", "set_edges", "set_years")
    doc = "Capex per distance for transport technologies."
    unit_category = {"money": 1, "distance": -1}
    dependencies = ["capex_specific_transport"]

    @classmethod
    def store_input_data(cls, element):
        """Retain the value loaded together with specific transport capex."""
