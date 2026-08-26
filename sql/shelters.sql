INSERT INTO shelters (name, address, email, state_code, phone, geom)
     VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) ON CONFLICT (id) DO NOTHING;