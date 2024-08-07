import argparse
from unittest import mock

from cmd_params import extract_cmd_params


class TestExtractCmdParams(object):
    @mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            input="../data/survey_results.csv",
        ),
    )
    def test_start_date(self, mock_args):
        result = extract_cmd_params()
        assert result == {
            "input": "../data/survey_results.csv",
        }
