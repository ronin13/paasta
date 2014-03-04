from contextlib import nested

import mock
import testify as T

import wizard
from service_wizard import autosuggest
from service_wizard import config


class SrvReaderWriterTestCase(T.TestCase):
    """I bailed out of this test, but I'll leave this here for now as an
    example of how to interact with the Srv* classes."""
    @T.setup
    def init_service(self):
        paths = wizard.paths.SrvPathBuilder("fake_srvpathbuilder")
        self.srw = wizard.SrvReaderWriter(paths)

class ValidateOptionsTestCase(T.TestCase):
    def test_enable_puppet_requires_puppet_root(self):
        parser = mock.Mock()
        options = mock.Mock()
        options.enable_puppet = True
        options.puppet_root = None
        options.enable_nagios = False # Disable checks we don't care about
        with T.assert_raises(SystemExit):
            wizard.validate_options(parser, options)

    def test_enable_nagios_requires_nagios_root(self):
        parser = mock.Mock()
        options = mock.Mock()
        options.enable_nagios = True
        options.nagios_root = None
        options.enable_puppet = False # Disable checks we don't care about
        with T.assert_raises(SystemExit):
            wizard.validate_options(parser, options)

class AutosuggestTestCase(T.TestCase):
    def test_suggest_port(self):
        # mock.patch was very confused by the config module, so I'm doing it
        # this way. One more reason to disapprove of this global config module
        # scheme.
        config.PUPPET_ROOT = "fake_puppet_root"

        walk_return = [(
            "fake_root",
            "fake_dir",
            [
                "fake_file", # ignored
                "repl_delay_reporter.yaml", # contains 'port' but ignored
                "port",
                "status_port",
                "weird_port", # has bogus out-of-range value
            ]
        )]
        mock_walk = mock.Mock(return_value=walk_return)

        # See http://www.voidspace.org.uk/python/mock/examples.html#multiple-calls-with-different-effects
        get_port_from_file_returns = [
            13001,
            13002,
            55555, # bogus out-of-range value
        ]
        def get_port_from_file_side_effect(*args):
            return get_port_from_file_returns.pop(0)
        mock_get_port_from_file = mock.Mock(side_effect=get_port_from_file_side_effect)
        with nested(
            mock.patch("os.walk", mock_walk),
            mock.patch("service_wizard.autosuggest._get_port_from_file", mock_get_port_from_file),
        ):
            actual = autosuggest.suggest_port()
        # Sanity check: our mock was called once for each legit port file in
        # walk_return
        T.assert_equal(mock_get_port_from_file.call_count, 3)

        # What we came here for: the actual output of the function under test
        T.assert_equal(actual, 13002 + 1) # highest port + 1

class GetServiceYamlContentsTestCase(T.TestCase):
    def test_empty(self):
        runs_on = ""
        deploys_on = ""
        actual = wizard.get_service_yaml_contents(runs_on, deploys_on)

        # Verify entire lines, e.g. to make sure that '---' appears as its own
        # line and not as part of 'crazy---service----name'.
        T.assert_in("---\n", actual)
        # I think a blank line would be better but I can't figure out how to
        # get pyyaml to emit that.
        T.assert_in("runs_on:\n- ''", actual)
        T.assert_in("deployed_to:\n- ''", actual)

    def test_one_runs_on(self):
        runs_on = "runs_on1"
        deploys_on = ""
        actual = wizard.get_service_yaml_contents(runs_on, deploys_on)

        expected = "runs_on:\n- %s" % runs_on
        T.assert_in(expected, actual)

    def test_two_runs_on(self):
        runs_on = "runs_on1,runs_on2"
        deploys_on = ""
        actual = wizard.get_service_yaml_contents(runs_on, deploys_on)

        expected = "runs_on:\n- %s\n- %s" % tuple(runs_on.split(","))
        T.assert_in(expected, actual)


if __name__ == "__main__":
    T.run()
