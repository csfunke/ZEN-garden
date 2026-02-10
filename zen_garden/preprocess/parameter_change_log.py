def parameter_change_log():
    log_dict = {
        "min_full_load_hours_fraction": {
            "default_value": 0,  # only 0, 1, or 'inf' are allowed
            "unit": "min_load",
        },
        "transport_limit_out": {
            "default_value": "inf",  # only 0, 1, or 'inf' are allowed
            "unit": "availability_import_yearly",
        },
        "transport_limit_in": {
            "default_value": "inf",  # only 0, 1, or 'inf' are allowed
            "unit": "availability_import_yearly",
        },
         "transport_limit_net": {
            "default_value": "inf",  # only 0, 1, or 'inf' are allowed
            "unit": "availability_import_yearly",
        }   
        #    "new_parameter_name": {
        #       "default_value": 0, # only 0, 1, or 'inf' are allowed
        #       "unit": "existing_parameter_name_with_same_unit"
        #   }
    }

    return log_dict
