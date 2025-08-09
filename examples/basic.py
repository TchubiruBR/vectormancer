# Example usage of vectormancer library API
from vectormancer import Vectormancer

vm = Vectormancer()
vm.index("./examples")
print(vm.query("example usage", top_k=3))