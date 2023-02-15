import pytest


@pytest.mark.parametrize(["size", "expected_output"],
                         [
                             (0, ("Zeer kort", "very-low")),
                             (1_000, ("Zeer kort", "very-low")),
                             (1_001, ("&nbsp;&nbsp;&nbsp;Kort&nbsp;&nbsp;&nbsp;", "low")),
                             (10_000, ("&nbsp;&nbsp;&nbsp;Kort&nbsp;&nbsp;&nbsp;", "low")),
                             (10_001, ("&nbsp;Middel&nbsp;", "middle")),
                             (100_000, ("&nbsp;Middel&nbsp;", "middle")),
                             (100_001, ("&nbsp;&nbsp;&nbsp;Lang&nbsp;&nbsp;&nbsp;", "high")),
                             (500_000, ("&nbsp;&nbsp;&nbsp;Lang&nbsp;&nbsp;&nbsp;", "high")),
                             (500_001, ("Zeer lang", "very-high")),
                         ])
def test_format_size(size, expected_output):
    from results_tab import format_size

    result_title, result_classname = format_size(size)
    expected_title, expected_classname = expected_output

    assert result_title == expected_title, "Get correct title for size"
    assert result_classname == expected_classname, "Get correct classname for size"


@pytest.mark.parametrize(["date", "expected_output"],
                         [
                             ("2022-01-01", "01-01-2022"),
                             ("2022-02-10T01:00", "10-02-2022"),
                             ("2022-03-20T01:00+0100", "20-03-2022")
                         ])
def test_format_date(date, expected_output):
    from results_tab import format_date

    assert format_date(date) == expected_output, "Format date correctly"
