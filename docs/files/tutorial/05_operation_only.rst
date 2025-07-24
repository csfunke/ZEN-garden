.. _t_operation_only.t_operation_only:

######################################
Tutorial 5: Operation-Only Simulations
######################################

In ZEN-garden, the main optimization problem can be followed by a 
operation-only optimization problem in which technology capacities are fixed
and only the operation of the system is optimized. In this section, this Setup
is hencefor refred to as a two-phase simulation. The two phases refer to:

- *Phase 1*: the standard ZEN-garden optimization problem in which both capacity 
  and operation are optimized concurrently. 
- *Phase 2*: an operation-only optimization problem in which technology 
  capacities are fixed at the levels determined in Phase 1.

The phase 2 problem yields the same variable values as the 
phase 1 problem in all variables except capacity additions. This is because
the phase 1 problem already optimizes operation. Nonetheless, the two 
problems yield different dual values. 

The operation-only phase 2 problem is particularly relevant for obtaining 
realistic carrier prices. Many carriers (e.g. electricity) follow marginal 
pricing schemes where the price is set by the marginal production cost. In this 
case, the dual value of the nodal energy balance in the phase 2 problem 
corresponds to the carrier price. The phase 1 dual value over-estimates the 
price since it includes capital costs.


.. note::

    To understand why phase 2 dual values correspond to prices, recall the 
    definition of the dual variables. The dual variable (:math:`\lambda`) of a 
    constraint :math:`g(x) = 0` with an objective :math:`f(x)` is defined as:

    .. math::

        \lambda = \frac{\partial f}{\partial g}

    For cost minimization problems, the dual variable of the energy balance
    constraint thus measures the increase in total system cost required to 
    supply one additional unit of the carrier. In the phase 1 problem, total 
    system costs includes variable costs, fixed costs, and capacity investments.
    When supplying an additional unit of the carrier requires additional 
    capacity, the dual value thus includes these capacity costs. In 
    contrast, the phase 2 problem treats capacity expenditures as fixed. Thus,
    only marginal costs of operation are reflected in the dual values. 


Setup
=====

The system configuration ``include_operation_only_phase`` activates the 
two-phase functionality. To include an operations-only phase in your simulation,
add the following entry to the ``system.json`` file:

.. code:: json

        { 
          // Additional system configurations go here
          "include_operation_only_phase": true
        }


Variables and duals from the phase 2 simulation are stored in the same output
files as the phase 1 simulation. The names of phase two variables and duals are
are stored with the suffix ``_operation`` to distinguish them from their phase 1
counterparts. 

The solver configuration ``selected_saved_duals`` allows users to choose which
dual values to save from both phases of the simulation. Similarly, the solver 
configurations ``selected_saved_variables`` and 
``selected_saved_variables_operation`` allow users to choose which variables 
to save from the phase 1 and phase 2 problems, respectively. These can be
added to the ``config.json`` file as follows:

.. code:: JSON
    
    {
      "analysis": {
        // Additional analysis fields go here
      },
      "solver": {
        // Additional solver fields go here
        "selected_saved_duals": ["constraint_nodal_energy_balance"],
        "selected_saved_variables_operation": ["flow_conversion_input", "storage_level"],
      }
    }


Example problem
===============



Two-phase simulations and myopic foresight
==========================================

In myopic foresight schemes, the 



