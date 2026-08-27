SELECT name, address, email, phone, ST_Y(geom::geometry), ST_X(geom::geometry) 
 FROM shelters 
 WHERE TRIM(UPPER(state_code)) = TRIM(UPPER(%s))
 
 --WHERE state_code = %s; 