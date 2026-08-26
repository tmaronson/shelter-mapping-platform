-- query.sql 
SELECT t.tract_id, c.name AS clinic_name, ST_Distance(ST_Centroid(t.geom)::geography, c.geom::geography) AS distance_meters FROM census_tracts t 
  CROSS JOIN LATERAL ( SELECT name, geom FROM clinics ORDER BY t.geom <-> geom LIMIT 1 ) c 
ORDER BY distance_meters DESC;