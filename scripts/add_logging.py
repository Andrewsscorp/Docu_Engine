import re

with open("app/main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

logging_setup = """
import logging
import sys

# ==============================================================
# PARTE 15: OBSERVABILIDAD Y LOGGING ESTRUCTURADO
# ==============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("docuengine_api.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("docuengine")
logger.info("Iniciando DocuEngine SGDEA (Observabilidad Activada)")

"""

if "logging.basicConfig(" not in main_code:
    main_code = main_code.replace("import os", "import os\n" + logging_setup)

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
