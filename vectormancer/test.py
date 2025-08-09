from vectormancer import Vectormancer
vm = Vectormancer()
vm.index("./examples")
print(vm.query("high frequency trading nasdaq", top_k=3))
