from acfo.__main__ import _sync_divisions, main


def test_cli_requires_command():
    try:
        main([])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected argparse to exit")


class _DivClient:
    def __init__(self):
        self.division = 10

    def divisions(self):
        return [{"Code": 10}, {"Code": 20}]


def test_sync_divisions_default_is_current():
    assert _sync_divisions(_DivClient(), all_divisions=False) == [10]


def test_sync_divisions_all_uses_exact_codes():
    assert _sync_divisions(_DivClient(), all_divisions=True) == [10, 20]
