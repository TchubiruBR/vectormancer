from vectormancer import Vectormancer

def test_smoke_import():
    import vectormancer
    assert hasattr(vectormancer, "Vectormancer")
