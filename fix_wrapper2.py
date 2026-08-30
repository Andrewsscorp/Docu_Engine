with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

old_str = """            {% endif %}
        </div>
    </section>"""

new_str = """            {% endif %}
            </div>
        </div>
        
        <div x-show="tab === 'expedientes'" x-cloak>
            <div id="expedientes-grid" class="mb-8">
                <!-- HTMX will load the expedientes list here -->
            </div>
        </div>
    </section>"""

content = content.replace(old_str, new_str)

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
