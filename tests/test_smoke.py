from vectormancer import Vectormancer

def test_smoke_import():
    import vectormancer
    assert hasattr(vectormancer, "Vectormancer")

def test_stats_smoke(tmp_path):
    vm = Vectormancer(persist_dir=str(tmp_path / ".index"))
    vm.index("examples")
    s = vm.store.stats()
    assert s["num_chunks"] >= 1
    assert s["dim"] > 0
