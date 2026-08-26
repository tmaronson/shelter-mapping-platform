-- populate.sql
TRUNCATE TABLE shelters, clinics, census_tracts RESTART IDENTITY CASCADE; 
INSERT INTO shelters (name, address, geom) VALUES ('Downtown Humane Shelter', '123 Main St, Atlanta, GA', ST_GeomFromText('POINT(-84.3880 33.7490)', 4326)), ('Northside Animal Haven', '456 Piedmont Rd, Atlanta, GA', ST_GeomFromText('POINT(-84.3680 33.8100)', 4326)); 
INSERT INTO clinics (name, address, geom) VALUES ('Midtown Spay Neuter Clinic', '789 Peachtree St, Atlanta, GA', ST_GeomFromText('POINT(-84.3850 33.7760)', 4326)); 
INSERT INTO census_tracts (tract_id, pet_density, geom) VALUES 
  ('Tract-A', 152.4, ST_Multi(ST_GeomFromText('POLYGON((-84.40 33.73, -84.37 33.73, -84.37 33.76, -84.40 33.76, -84.40 33.73))', 4326))), 
  ('Tract-B', 48.7, ST_Multi(ST_GeomFromText('POLYGON((-84.37 33.79, -84.34 33.79, -84.34 33.82, -84.37 33.82, -84.37 33.79))', 4326))); 