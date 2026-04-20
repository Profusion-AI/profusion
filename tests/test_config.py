"""Config and adapter import safety tests.

These must pass without a live ANTHROPIC_API_KEY.
"""

import os

import pytest


def test_config_loads_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import importlib
    import orchestrator.config as config
    importlib.reload(config)
    assert config.ANTHROPIC_API_KEY is None or config.ANTHROPIC_API_KEY == ""


def test_claude_adapter_imports_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from orchestrator.adapters import claude
    assert callable(claude.generate)
    assert issubclass(claude.MissingAPIKeyError, Exception)


def test_claude_generate_raises_missing_key_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import orchestrator.config as config
    config.ANTHROPIC_API_KEY = None

    from orchestrator.adapters.claude import MissingAPIKeyError, generate
    with pytest.raises(MissingAPIKeyError):
        generate(system="test", user="test")


def test_claude_missing_key_error_is_not_attribute_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import orchestrator.config as config
    config.ANTHROPIC_API_KEY = None

    from orchestrator.adapters.claude import MissingAPIKeyError, generate
    try:
        generate(system="test", user="test")
    except MissingAPIKeyError:
        pass
    except AttributeError as e:
        pytest.fail(f"Should raise MissingAPIKeyError, not AttributeError: {e}")


def test_stub_adapters_import_cleanly():
    from orchestrator.adapters import firecrawl, turbo, v2
    assert callable(turbo.render)
    assert callable(v2.publish)
    assert callable(firecrawl.scrape)


def test_stub_adapters_raise_not_implemented():
    from orchestrator.adapters import firecrawl
    with pytest.raises(NotImplementedError):
        firecrawl.scrape("https://example.com")
