import torch
x = torch.randn(1024,1024, device="cuda")
y = x @ x
print("ok:", y.norm().item())