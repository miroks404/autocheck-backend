from app.checking.calculator import ResultCalculator
from app.checking.interfaces import CheckResultDTO


def test_result_calculator_weighted_score():
    results = [
        CheckResultDTO(checker="build", status="passed", score=100, message="", details={}),
        CheckResultDTO(checker="tests", status="passed", score=50, message="", details={}),
    ]
    weights = {"build": 2, "tests": 1}
    assert ResultCalculator.total_score(results, weights) == 83
