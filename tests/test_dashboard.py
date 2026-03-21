import pytest


@pytest.mark.sanity
@pytest.mark.smoke
@pytest.mark.regression
def test_dashboard_title(dashboard_page):
    assert dashboard_page.get_page_title() == "Logged In Successfully"
