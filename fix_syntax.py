with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('xml_content += "  </ListaDocumentos>\n"', 'xml_content += "  </ListaDocumentos>\\n"')
# Also fix the weird newline that got inserted!
content = content.replace('xml_content += "  </ListaDocumentos>\n"', 'xml_content += "  </ListaDocumentos>\\n"')

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
