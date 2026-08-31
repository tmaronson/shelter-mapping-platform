SELECT DISTINCT(c.name),
	   c.address, 
	   c.phone, 
	   ROUND((ST_Distance(ST_Centroid(t.geom)::geography,
	   c.geom::geography) / 1609.34)::numeric, 1) AS distance_miles 
FROM census_tracts t 
CROSS JOIN clinics c 
WHERE t.tract_id = %s 
ORDER BY distance_miles ASC LIMIT 5; 