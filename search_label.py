with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for line in lines:
    if 'Fondo' in line and 'label' in line:
        print(line.strip())
