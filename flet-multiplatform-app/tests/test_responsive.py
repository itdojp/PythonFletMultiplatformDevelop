import pytest
from src.utils.responsive_utils import calculate_responsive_layout

def test_calculate_responsive_layout_mobile():
    width = 500
    expected_layout = {
        'columns': 1,
        'item_width': 100,
        'item_height': 150
    }
    layout = calculate_responsive_layout(width)
    assert layout == expected_layout

def test_calculate_responsive_layout_tablet():
    width = 800
    expected_layout = {
        'columns': 2,
        'item_width': 350,
        'item_height': 150
    }
    layout = calculate_responsive_layout(width)
    assert layout == expected_layout

def test_calculate_responsive_layout_desktop():
    width = 1200
    expected_layout = {
        'columns': 3,
        'item_width': 350,
        'item_height': 150
    }
    layout = calculate_responsive_layout(width)
    assert layout == expected_layout

def test_calculate_responsive_layout_large_desktop():
    width = 1600
    expected_layout = {
        'columns': 4,
        'item_width': 350,
        'item_height': 150
    }
    layout = calculate_responsive_layout(width)
    assert layout == expected_layout