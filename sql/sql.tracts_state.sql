SELECT tract_id, pet_density, ST_AsGeoJSON(ST_SimplifyPreserveTopology(geom, 0.001)) 
FROM census_tracts 
WHERE tract_id LIKE %s; 