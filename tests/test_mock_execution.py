import pytest
from unittest.mock import patch
from alpss.alpss_main import alpss_main
import matplotlib.pyplot as plt


def test_alpss_main_success(valid_inputs):
    with patch("alpss.utils.phases.spall_doi_finder") as mock_spall_doi_finder, patch(
        "alpss.utils.phases.carrier_frequency"
    ) as mock_carrier_frequency, patch(
        "alpss.utils.phases.carrier_filter"
    ) as mock_carrier_filter, patch(
        "alpss.utils.phases.velocity_calculation"
    ) as mock_velocity_calculation, patch(
        "alpss.utils.phases.instantaneous_uncertainty_analysis"
    ) as mock_iua, patch(
        "alpss.utils.phases.spall_analysis"
    ) as mock_spall_analysis, patch(
        "alpss.utils.phases.full_uncertainty_analysis"
    ) as mock_fua, patch(
        "alpss.utils.phases.plot_results"
    ) as mock_plotting, patch(
        "alpss.utils.phases.save"
    ) as mock_saving:

        mock_plotting.return_value = plt.Figure()
        mock_saving.return_value = dict()

        result = alpss_main(**valid_inputs)

        assert isinstance(result[0], plt.Figure)
        assert isinstance(result[1], dict)

        mock_spall_doi_finder.assert_called_once()
        mock_carrier_frequency.assert_called_once()
        mock_carrier_filter.assert_called_once()
        mock_velocity_calculation.assert_called_once()
        mock_iua.assert_called_once()
        mock_spall_analysis.assert_called_once()
        mock_fua.assert_called_once()
        mock_plotting.assert_called_once()
        mock_saving.assert_called_once()
