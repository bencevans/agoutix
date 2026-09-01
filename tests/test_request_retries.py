from unittest.mock import Mock

import requests

from agoutix.agouti import Agouti


def client_without_login():
    client = object.__new__(Agouti)
    client.verbose = False
    return client


def test_network_errors_use_capped_exponential_backoff_with_jitter(monkeypatch):
    request = Mock(
        side_effect=[
            requests.RequestException("temporary"),
            requests.RequestException("temporary"),
            Mock(status_code=200),
        ]
    )
    sleep = Mock()
    uniform = Mock(side_effect=lambda minimum, maximum: maximum)
    monkeypatch.setattr("agoutix.agouti.request", request)
    monkeypatch.setattr("agoutix.agouti.time.sleep", sleep)
    monkeypatch.setattr("agoutix.agouti.random.uniform", uniform)

    response = client_without_login()._request_with_retries(
        "GET",
        "https://example.test",
        retry_delay_seconds=2,
        max_retry_delay_seconds=3,
    )

    assert response.status_code == 200
    assert [call.args for call in uniform.call_args_list] == [(0, 2), (0, 3)]
    assert [call.args[0] for call in sleep.call_args_list] == [2, 3]


def test_retry_after_is_respected(monkeypatch):
    responses = [
        Mock(status_code=429, headers={"Retry-After": "10"}),
        Mock(status_code=200, headers={}),
    ]
    sleep = Mock()
    monkeypatch.setattr("agoutix.agouti.request", Mock(side_effect=responses))
    monkeypatch.setattr("agoutix.agouti.time.sleep", sleep)
    monkeypatch.setattr("agoutix.agouti.random.uniform", Mock(return_value=0.25))

    response = client_without_login()._request_with_retries(
        "GET", "https://example.test"
    )

    assert response.status_code == 200
    sleep.assert_called_once_with(10.0)


def test_retries_until_configurable_time_budget_expires(monkeypatch):
    request = Mock(side_effect=requests.RequestException("offline"))
    sleep = Mock()
    monotonic = Mock(side_effect=[100, 105, 120])
    monkeypatch.setattr("agoutix.agouti.request", request)
    monkeypatch.setattr("agoutix.agouti.time.sleep", sleep)
    monkeypatch.setattr("agoutix.agouti.time.monotonic", monotonic)
    monkeypatch.setattr("agoutix.agouti.random.uniform", Mock(return_value=60))

    client = client_without_login()
    client.MAX_RETRY_DURATION_SECONDS = 20

    try:
        client._request_with_retries("GET", "https://example.test")
    except Exception as error:
        assert str(error) == "Request failed after retrying for 20 seconds"
    else:
        raise AssertionError("Expected the retry time budget to expire")

    assert request.call_count == 2
    sleep.assert_called_once_with(15)
