def parameter_change_log():
    log_dict = {
      "min_average_capacity_factor": {
           "default_value": 'inf', # only 0, 1, or 'inf' are allowed
           "unit": "min_load"
      }
    #    "new_parameter_name": {
     #       "default_value": 0, # only 0, 1, or 'inf' are allowed
     #       "unit": "existing_parameter_name_with_same_unit"
     #   }
    }

    return log_dict