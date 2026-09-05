import os

dirs = [
    "backend/src/domain/entities",
    "backend/src/domain/interfaces",
    "backend/src/application/use_cases",
    "backend/src/application/dtos",
    "backend/src/infrastructure/database",
    "backend/src/infrastructure/repositories",
    "backend/src/infrastructure/messaging",
    "backend/src/infrastructure/agents",
    "backend/src/infrastructure/security",
    "backend/src/presentation/controllers",
    "backend/src/presentation/routes",
    "backend/src/presentation/middlewares",
    "frontend/src/router",
    "frontend/src/layouts",
    "frontend/src/core",
    "frontend/src/auth",
    "frontend/src/features/ocr-processor",
    "frontend/src/features/user-management",
    "frontend/src/features/dashboard",
    "docker/postgres",
    "docker/api-gateway"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    # create a .gitkeep so empty folders are tracked if using git
    with open(os.path.join(d, ".gitkeep"), "w") as f:
        pass

print("Structure created successfully.")
