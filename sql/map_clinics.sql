-- map_clinics.sql
SELECT name, ST_Y(geom::geometry), ST_X(geom::geometry) FROM clinics;
