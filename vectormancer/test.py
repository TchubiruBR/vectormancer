from vectormancer import Vectormancer
vm = Vectormancer()
vm.index("./examples")
print(vm.query("capital of France", top_k=3))
root@C.24834382:~/vectormancer$ python vectormancer/test.py
[{'id': '/root/vectormancer/examples/test.txt', 'text': 'The capital of France is Paris.\n', 'score': 0.907939076423645, 'path': '/root/vectormancer/examples/test.txt', 'snippet': 'The capital of France is Paris.\n'}, {'id': '/root/vectormancer/examples/basic.py', 'text': '# Example usage of vectormancer library API\nfrom vectormancer import Vectormancer\n\nvm = Vectormancer()\nvm.index("./examples")\nprint(vm.query("example usage", top_k=3))', 'score': 0.014571936801075935, 'path': '/root/vectormancer/examples/basic.py', 'snippet': '# Example usage of vectormancer library API\nfrom vectormancer import Vectormancer\n\nvm = Vectormancer()\nvm.index("./examples")\nprint(vm.query("example usage", top_k=3))'}