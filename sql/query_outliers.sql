WITH ranked_tracts AS 
	( SELECT 
	  t.tract_id,
	  t.pet_density,
	  c.name AS clinic_name,
	  ST_Distance(ST_Centroid(t.geom)::geography, c.geom::geography) AS distance_meters,
	  NTILE(5) OVER (ORDER BY t.pet_density) AS density_bucket,
	  NTILE(5) OVER (ORDER BY ST_Distance(ST_Centroid(t.geom)::geography, c.geom::geography)) AS distance_bucket
	FROM census_tracts 
	  t CROSS JOIN LATERAL 
    ( SELECT name, geom FROM clinics ORDER BY t.geom <-> geom LIMIT 1 ) c ) 
	
SELECT tract_id, pet_density, clinic_name, distance_meters / 1609.34 AS distance_miles 
  FROM ranked_tracts 
WHERE density_bucket = 5 AND distance_bucket = 5 
ORDER BY pet_density DESC;