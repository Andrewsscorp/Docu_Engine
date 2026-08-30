INSERT INTO permissions (name, description)
VALUES ('tipologias:crear', 'Permite crear nuevas tipologías en el catálogo maestro TRD')
ON CONFLICT (name) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'Admin' AND p.name = 'tipologias:crear'
ON CONFLICT DO NOTHING;
