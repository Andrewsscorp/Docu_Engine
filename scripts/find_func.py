import ast
import sys

with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    source = f.read()

parsed = ast.parse(source)
for node in parsed.body:
    if isinstance(node, ast.AsyncFunctionDef) and node.name == "cerrar_expediente":
        start = node.lineno
        end = node.end_lineno
        print(f"Starts at {start}, ends at {end}")
        lines = source.splitlines()
        print("\n".join(lines[start-1:start+10]))
        print("...")
        print("\n".join(lines[end-10:end]))
        break
