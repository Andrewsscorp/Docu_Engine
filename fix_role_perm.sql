INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'SuperAdmin' AND p.name = 'tipologias:crear'
ON CONFLICT DO NOTHING;
