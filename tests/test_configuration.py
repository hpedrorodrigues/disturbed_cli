import pytest

from disturbed.configuration import Configuration, Provider


def write_config(tmp_path, provider_line: str = "") -> str:
    path = tmp_path / "config.yaml"
    path.write_text(
        "schedules_mapping:\n" "  - schedule_name: sre\n" "    user_group_name: 'sre-oncall'\n" + provider_line
    )
    return str(path)


def test_provider_defaults_to_pagerduty(tmp_path):
    config = Configuration(path=write_config(tmp_path))

    assert config.schedules_mapping[0].provider == Provider.PAGERDUTY


def test_provider_parses_opsgenie(tmp_path):
    config = Configuration(path=write_config(tmp_path, provider_line="    provider: opsgenie\n"))

    assert config.schedules_mapping[0].provider == Provider.OPSGENIE


def test_provider_parses_pagerduty(tmp_path):
    config = Configuration(path=write_config(tmp_path, provider_line="    provider: pagerduty\n"))

    assert config.schedules_mapping[0].provider == Provider.PAGERDUTY


def test_invalid_provider_exits(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        Configuration(path=write_config(tmp_path, provider_line="    provider: pagerdooty\n"))

    assert exc_info.value.code == 1
