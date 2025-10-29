import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.numbers_analysis import (
    TASKS,
    NumberToken,
    count_tokens,
    extract_number_tokens,
    longest_token,
    max_token,
    sum_tokens,
)


@pytest.fixture
def sample_text():
    return "356xv@@4vdfvdfD#$%@@#245"


def test_extract_number_tokens(sample_text):
    tokens = extract_number_tokens(sample_text)
    assert [token.text for token in tokens] == ["356", "4", "245"]


def test_count_tokens(sample_text):
    tokens = extract_number_tokens(sample_text)
    assert count_tokens(tokens) == "3"


def test_sum_tokens(sample_text):
    tokens = extract_number_tokens(sample_text)
    assert sum_tokens(tokens) == str(356 + 4 + 245)


def test_max_token(sample_text):
    tokens = extract_number_tokens(sample_text)
    assert max_token(tokens) == "356"


def test_longest_token(sample_text):
    tokens = extract_number_tokens(sample_text)
    assert longest_token(tokens) == "356 3"


def test_tasks_registry_contains_expected_functions():
    assert set(TASKS) == {"count", "sum", "max", "longest"}
    tokens = [NumberToken("001"), NumberToken("20")]
    assert TASKS["count"](tokens) == "2"
    assert TASKS["sum"](tokens) == str(1 + 20)
    assert TASKS["max"](tokens) == "20"
    assert TASKS["longest"](tokens) == "001 3"


def test_handles_input_without_numbers():
    tokens = extract_number_tokens("abc")
    assert count_tokens(tokens) == "0"
    assert sum_tokens(tokens) == "0"
    assert max_token(tokens) == "BRAK"
    assert longest_token(tokens) == "BRAK"
