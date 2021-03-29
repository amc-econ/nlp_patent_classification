#!/usr/bin/env python

"""Tests for `nlp_patent_classification` package."""


import unittest
from click.testing import CliRunner

from nlp_patent_classification import nlp_patent_classification
from nlp_patent_classification import cli


class TestNlp_patent_classification(unittest.TestCase):
    """Tests for `nlp_patent_classification` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'nlp_patent_classification.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
