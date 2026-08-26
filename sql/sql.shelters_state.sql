SELECT name, address, email, phone, ST_Y(geom::geometry), ST_X(geom::geometry) 
 FROM shelters 
 WHERE state_code = %s;    