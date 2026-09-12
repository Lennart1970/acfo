from acfo.__main__ import main


def test_cli_requires_command():
    try:
        main([])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected argparse to exit")
