SELECT tract_id, pet_density, ST_AsGeoJSON(geom) 
FROM census_tracts 
WHERE tract_id = %s;