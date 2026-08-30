with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_block = """    except Exception as e:
        # Fallback raw query if the view hasn't been created yet by the admin
        fallback_sql = \"\"\"
        SELECT"""

new_block = """    except Exception as e:
        # Transaction is aborted due to missing view, so we must rollback before running fallback query
        await db.rollback()
        # Fallback raw query if the view hasn't been created yet by the admin
        fallback_sql = \"\"\"
        SELECT"""

content = content.replace(old_block, new_block)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
