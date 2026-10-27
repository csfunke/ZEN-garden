"""Storage technology expressions."""

from zen_garden.model.component_types.expression import GenericExpression

from .charging_mode_capacity_limit import ChargingModeCapacityLimit
from .storage_energy_capacity_addition import StorageEnergyCapacityAddition
from .storage_level_change_after_self_discharge import (
    StorageLevelChangeAfterSelfDischarge,
)
from .storage_net_energy_inflow import StorageNetEnergyInflow
from .storage_overnight_capex import StorageOvernightCapex
from .storage_power_capacity_addition import StoragePowerCapacityAddition
from .storage_power_capacity_limit import StoragePowerCapacityLimit
from .storage_throughput import StorageThroughput

STORAGE_TECHNOLOGY_EXPRESSIONS: list[type[GenericExpression]] = [
    StorageThroughput,
    StoragePowerCapacityAddition,
    StorageEnergyCapacityAddition,
    StoragePowerCapacityLimit,
    ChargingModeCapacityLimit,
    StorageLevelChangeAfterSelfDischarge,
    StorageNetEnergyInflow,
    StorageOvernightCapex,
]

__all__ = [
    "ChargingModeCapacityLimit",
    "STORAGE_TECHNOLOGY_EXPRESSIONS",
    "StorageEnergyCapacityAddition",
    "StorageLevelChangeAfterSelfDischarge",
    "StorageNetEnergyInflow",
    "StorageOvernightCapex",
    "StoragePowerCapacityAddition",
    "StoragePowerCapacityLimit",
    "StorageThroughput",
]
