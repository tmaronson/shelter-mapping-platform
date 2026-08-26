 SELECT name, address, email, phone, ST_Y(geom::geometry), ST_X(geom::geometry) 
 FROM clinics 
 WHERE state_code = %s; 
