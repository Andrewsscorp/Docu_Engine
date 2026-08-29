with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
imports_to_move = [
    "from fastapi import Form, UploadFile, File, HTTPException\n",
    "import json\n",
    "from pydantic import BaseModel\n",
    "from typing import Optional\n"
]

# Write standard imports at the very beginning (after existing fastapi imports)
for line in lines:
    if line.startswith("from fastapi import APIRouter, Depends, Request"):
        new_lines.append(line)
        new_lines.extend(imports_to_move)
    elif line in imports_to_move:
        continue # Skip where they were injected
    else:
        new_lines.append(line)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
