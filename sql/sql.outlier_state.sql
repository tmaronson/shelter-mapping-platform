SELECT tract_id, pet_density 
FROM census_tracts 
WHERE tract_id LIKE %s;