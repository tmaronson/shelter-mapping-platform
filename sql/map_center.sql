SELECT ST_Y(ST_Centroid(ST_Extent(geom)::geometry)), ST_X(ST_Centroid(ST_Extent(geom)::geometry)) 
FROM census_tracts 
WHERE tract_id LIKE %s