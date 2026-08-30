with open("docker-compose.yml", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("      dockerfile: Dockerfile.ocr\n        environment:", "      dockerfile: Dockerfile.ocr\n    environment:")

with open("docker-compose.yml", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed docker-compose.yml")
