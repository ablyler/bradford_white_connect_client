from typing import List

from .constants import BradfordWhiteConnectHeatingModes


class BradfordWhiteConnectHelper:
    @staticmethod
    def get_appliance_model_heating_modes(appliance_model: str) -> List[int]:
        """
        This function returns the heating modes available for a given appliance model.

        Parameters:
        appliance_model (str): The model number of the appliance.

        Returns:
        List[int]: A list of heating modes available for the appliance model. The heating modes are represented as integers.

        The function checks if the provided model number is in the list of model numbers that do not support the Hybrid Plus mode.
        If the model number is in the list, the function returns a list of heating modes excluding the Hybrid Plus mode.
        Otherwise, it returns a list of heating modes including the Hybrid Plus mode.

        The heating modes are sourced from the BradfordWhiteConnectHeatingModes enumeration.

        Note: The model numbers are sourced from:
        https://forthepro.bradfordwhite.com/our-products/usa-residential-heat-pump/aerotherm-series-heat-pump/
        """

        model_numbers_without_hybrid_plus = [
            "RE2H50S10-1NCWT",
            "RE2H65T10-1NCWT",
            "RE2H80T10-1NCWT",
        ]

        # return the heating modes based on the model number
        if appliance_model in model_numbers_without_hybrid_plus:
            return [
                BradfordWhiteConnectHeatingModes.ELECTRIC,
                BradfordWhiteConnectHeatingModes.HEAT_PUMP,
                BradfordWhiteConnectHeatingModes.VACATION,
                BradfordWhiteConnectHeatingModes.HYBRID,
            ]
        else:
            return [
                BradfordWhiteConnectHeatingModes.ELECTRIC,
                BradfordWhiteConnectHeatingModes.HEAT_PUMP,
                BradfordWhiteConnectHeatingModes.VACATION,
                BradfordWhiteConnectHeatingModes.HYBRID,
                BradfordWhiteConnectHeatingModes.HYBRID_PLUS,
            ]
