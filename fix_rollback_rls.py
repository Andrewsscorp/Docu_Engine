with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_except = """    except Exception as e:
        # Transaction is aborted due to missing view, so we must rollback before running fallback query
        await db.rollback()
        # Fallback raw query if the view hasn't been created yet by the admin"""

new_except = """    except Exception as e:
        # Transaction is aborted due to missing view, so we must rollback before running fallback query
        await db.rollback()
        # Re-apply RLS config because rollback clears it!
        await db.execute(
            text("SELECT set_config('app.current_tenant', :tenant, false)"), 
            {"tenant": session_data["tenant_id"]}
        )
        if session_data.get("user_id"):
            await db.execute(
                text("SELECT set_config('app.current_user_id', :uid, false)"), 
                {"uid": session_data["user_id"]}
            )
        # Fallback raw query if the view hasn't been created yet by the admin"""

content = content.replace(old_except, new_except)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
