import pandas as pd
from constants.machines.home_heating import (
    CENTRAL_SYSTEMS,
)


def assimilate_other_heating(response: pd.Series) -> pd.Series:
    heating_type = response['home_heating_other_closest_match']
    # If they didn't have an "Other" value, leave it as is.
    if pd.isna(heating_type):
        return response

    updated_response = response.copy()
    # If the "other" heating is a central system, check if that particular type of central system has been selected.
    if heating_type in CENTRAL_SYSTEMS:
        # If yes, ignore so that we don't double-count the same time of central heating system
        if response[heating_type] > 0:
            return response
        # If no, change their response to select the central heating system
        updated_response[heating_type] = 1
        return updated_response

    # If it's an individual system, increment
    updated_response[heating_type] += 1
    return updated_response
