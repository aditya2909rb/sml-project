from sml.mrna_designer import MRNAVaccineDesigner, StabilityOptimizer


def test_gc_tuning_increases_low_gc_sequence_into_window() -> None:
    optimizer = StabilityOptimizer()
    optimized = optimizer.optimize_stability("A" * 240)
    gc = optimizer._calculate_gc_content(optimized)
    assert 0.40 <= gc <= 0.60


def test_gc_tuning_decreases_high_gc_sequence_into_window() -> None:
    optimizer = StabilityOptimizer()
    optimized = optimizer.optimize_stability("G" * 240)
    gc = optimizer._calculate_gc_content(optimized)
    assert 0.40 <= gc <= 0.60


def test_designed_construct_gc_content_within_window() -> None:
    designer = MRNAVaccineDesigner()
    construct = designer.design_vaccine(["SIINFEKL", "GILGFVFTL"], include_self_learning=False)
    assert 0.40 <= construct.gc_content <= 0.60
