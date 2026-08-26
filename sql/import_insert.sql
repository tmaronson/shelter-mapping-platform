INSERT INTO census_tracts (tract_id, pet_density, geom) 
  VALUES (%s, %s, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)));