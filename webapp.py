### import json 
from pathlib import Path
import psycopg2
from jproperties import Properties
import folium
from geopy.geocoders import Nominatim 
import time
import json
import csv 
from folium.plugins import MarkerCluster
import streamlit as st 
import re
from streamlit_folium import st_folium, folium_static
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_DIR = Path(__file__).parent.resolve()
SQL_DIR = PROJECT_DIR / "sql" 

# Load config.properties using jproperties 
p = Properties() 
with open(PROJECT_DIR / "config.properties", "rb") as f:
    p.load(f) 
    DB_CONN = os.getenv("DATABASE_URL")
    #DB_CONN = p.get(str("database.connection_string")).data # Connect to database.
    #GEOJSON_PATH = p.get("data.geojson_path").data # data file
    SCHEMA_FILE = p.get("sql.schema").data # Create tables and extension.
    #POPULATE_FILE = p.get("sql.populate").data # Populate tables.
    QUERY_FILE = p.get("sql.query").data # Select data from tables.
    TRUNCATE_FILE = p.get("sql.truncate").data # Truncate table census_tracts.
    TRACTS_FILE = p.get("sql.import").data # Populate census_tracts table.
    MAP_CLINICS_FILE = p.get("sql.map_clinics").data # Select data to map clinics.
    MAP_SHELTERS_FILE = p.get("sql.map_shelters").data # Select data to map shelters.
    SHELTERS_FILE = p.get("sql.shelters").data 
    CLINICS_FILE = p.get("sql.clinics").data
    MAP_CENTER_FILE = p.get("sql.map_center").data
    QUERY_OUTLIER_FILE = p.get("sql.query_outlier").data
    QUERY_BOXPLOT_FILE = p.get("sql.boxplot_query").data
    CENSUS_TRACTS = p.get("census_tracts")
    PET_DENSITY = p.get("sql.pet_density").data
    PETFINDER_FILE = p.get("data.petfinder_csv").data
    MAP_CLINICS_STATE_FILE = p.get("sql.clinics_state").data
    MAP_SHELTERS_STATE_FILE = p.get("sql.shelters_state").data
    MAP_TRACTS_STATE_FILE = p.get("sql.tracts_state").data
    OUTLIER_FILE = p.get("sql.outlier_state").data
    
@st.cache_data 
def load_fips_map(file_name):
    fips_map = {} 
    try:
        csv_path = PROJECT_DIR / file_name 
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f) 
            for row in reader: 
                # Adjust these keys to match CSV headers exactly s
                state_code = row.get("Abbreviation", "").upper().strip() 
                fips_code = row.get("FIPS", "").strip().zfill(2) 
                if state_code and fips_code: 
                    fips_map[state_code] = fips_code
        
        return fips_map
    except Exception as e: 
        print(f"Error loading state FIPS mapping: {e}")
        return {}

def read_sql_file(script_name):
    try:
        sql_path = SQL_DIR / script_name 
        with open(sql_path, "r") as f:
            return f.read() 
    except Exception as e: 
        print(f"Error reading SQL file {script_name}: {e}") 
        return ""
   
def run_sql_script(cur, script_name): 
    sql_query = read_sql_file(script_name)
    cur.execute(sql_query)
    print(f"Executed {script_name} successfully")
    
def import_tracts_from_geojson(cur, file_path, insert_sql, table_name): 
    # Load the generic SQL truncate template
    # truncate_template = read_sql_file(TRUNCATE_FILE)
    # cur.execute(truncate_template.format(table_name=table_name))
    # run_sql_script(cur, TRUNCATE_FILE)
    with open(PROJECT_DIR / file_path, "r") as f:
        geojson_data = json.load(f) 
        for feature in geojson_data["features"]:
            properties = feature["properties"] 
            tract_id = properties.get("GEOID", "Unknown") 
            population = float(properties.get("P0010001", 0))
            # Estimate households and total pet density (rounded) 
            estimated_households = population/2.5 
            pet_density = int(round(estimated_households * 0.63, 0))
            geom_dict = feature["geometry"] 
            geom_json_str = json.dumps(geom_dict) 
            # Execute the query template using loaded insert_sql variable
            cur.execute(insert_sql, (tract_id, pet_density, geom_json_str))
            #print(f"Successfully imported tracts from {file_path}") 
            
      
def get_heat_color(density): 
    if density > 800:
        return "#7f0000" 
    elif density > 500:
        return "#d7301f" 
    elif density > 200: 
        return "#ff5500" 
    elif density > 100: 
        return "#fdbb84" 
    elif density > 50: 
        return "#fdd49e" 
    else: 
        return "#fef0d9"
    

def add_census_tracts_to_map(m, fips_prefix): 
    try: 
        # 1. Create a dedicated FeatureGroup for the tracts
        tract_group = folium.FeatureGroup(name="Census Tracts", control=True).add_to(m) 
        geojson_data = get_cached_geojson_data(fips_prefix) 
        if not geojson_data["features"]: 
            return 
        # 2. Add the GeoJson layer directly to the tract_group instead of m
        folium.GeoJson( geojson_data, style_function=lambda x: 
                       { 
                          "fillColor": get_heat_color(x["properties"]["pet_density"]
                                                     ),
                                          "color": "black",
                                          "weight": 0.5,
                                           "fillOpacity": 0.4 
                        },
                                            tooltip=folium.GeoJsonTooltip( fields=["tract_id", "pet_density"],
                                            aliases=["Tract ID:", "Estimated Pets:"], localize=True ) ).add_to(tract_group)
        print("Successfully added census tract layer group.") 
    except Exception as e:
        print(f"Error loading tract polygons: {e}")

def local_css(file_name): 
    with open(PROJECT_DIR / file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
# Get legend as a list of tuples.
legend_items = [ ("Over 800 (Extremely High)", "#7f0000"), 
               ("501 to 800 (High)", "#d7301f"), 
               ("201 to 500 (Moderate-High)", "#ff5500"), 
               ("101 to 200 (Moderate)", "#fdbb84"), 
               ("51 to 100 (Low-Moderate)", "#fdd49e"), 
               ("0 to 50 (Low)", "#fef0d9") 
              ]
        
local_css("style.css") # Get stylesheet
st.sidebar.title("Shelter Analysis Legend")
# Added for radio button clinics or shelters
view_selection = st.sidebar.radio( "Show on Map", ["Both", "Shelters Only", "Clinics Only"] )
 
st.sidebar.subheader("Estimated Pet Density")

for label, color in legend_items: 
    st.sidebar.markdown(
                          f'<div class="legend-item">'
                          f'<div class="color-box" style="background-color: {color};"></div>'
                          f'<span class="legend-label">{label}</span>'
                          f'</div>', unsafe_allow_html=True
                        )

# not used            
def load_population_and_join_data(cur): 
     try:
         # Create the temporary population table 
         cur.execute(""" CREATE TABLE IF NOT EXISTS georgia_population ( tract_id VARCHAR(50) PRIMARY KEY, population INTEGER ); """) 
        # Clear any old population data
         cur.execute("TRUNCATE TABLE georgia_population;")
        # Load the population CSV file 
         csv_path = PROJECT_DIR / p.get("data.population_csv").data
         with open(csv_path, "r", encoding="utf-8") as f: 
             reader = csv.DictReader(f) 
             for row in reader:
                 cur.execute(""" INSERT INTO georgia_population (tract_id, population) VALUES (%s, %s) ON CONFLICT (tract_id) 
                      DO UPDATE SET population = EXCLUDED.population; """ ,
                          ( row['GEO_ID'][-11:], int(row['P1_001N']))) 
                # Run the SQL join script to update pet_density 
             join_query = read_sql_file(p.get("sql.join_population").data) 
             cur.execute(join_query) 
             print("Successfully loaded population data and updated tract pet densities.") 
     except Exception as e: 
         print(f"Error executing population join: {e}")
     
def load_progressive_shelters(cur, csv_file_name, sql_file_name, use_paid_api=False, api_key=None):
    try: 
        # Load the SQL insert template from properties 
        sql_query = read_sql_file(SHELTERS_FILE)
        #truncate_template = read_sql_file(TRUNCATE_FILE) 
        #cur.execute(truncate_template.format(table_name="shelters"))
        if use_paid_api and api_key: 
            from geopy.geocoders import OpenCage
            geolocator = OpenCage(api_key=api_key, timeout=10) 
        else: 
            geolocator = Nominatim(user_agent="shelter_locator_progressive", timeout=10) 
        csv_path = PROJECT_DIR / PETFINDER_FILE
        loaded_count = 0
    
        with open(csv_path, "r", encoding="utf-8") as f: 
                reader = csv.DictReader(f) 
                for row in reader: 
                   # Only geocode Georgia shelters
                    if row["id"].startswith("GA"): 
                        name = row["name"]
                    # Build the address string 
                        addr1 = row.get("address1", "").strip() 
                        addr2 = row.get("address2", "").strip()
                        address = f"{addr1}, {addr2}".strip(", ")
                        state_code = row.get("id", "")[:2].upper().strip()
                        website = row.get("website", "").strip()
                        if not address:
                            address = "Georgia, US" 
                        lat_val = row.get("latitude") or row.get("lat") or row.get("y") 
                        lon_val = row.get("longitude") or row.get("lon") or row.get("x") 
                        if (lat_val and lon_val) and (lat_val != "") and (lon_val != ""):
                            # Directly load coordinates
                            lat, lon = float(lat_val), float(lon_val) 
                            cur.execute(sql_query, (name, address, state_code, website, lon, lat)) 
                            loaded_count += 1 
                        else: 
                            # Use geocoding fallback
                            if not use_paid_api: 
                                time.sleep(1) 
                            clean_address = re.sub(r"(?i)P.?O.?\sBox\s\d+", "", address).strip(", ") 
                            location = geolocator.geocode(clean_address) 
                            if not location and "," in address: 
                                address_parts = address.split(",")
                                if len(address_parts) >= 2:
                                    fallback_query = ",".join(address_parts[-2:]).strip() 
                                    location = geolocator.geocode(fallback_query) 
                            if location:
                                lat, lon = location.latitude, location.longitude
                                cur.execute(sql_query, (name, address, state_code, website, lon, lat)) 
                                loaded_count += 1 
                                print(f"Geocoded Fallback: {name}") 
                            else: 
                                print(f"Could not resolve: {name}") 
        print(f"Successfully loaded {loaded_count} progressive shelters.")
    except Exception as e:
        print(f"Error in progressive loader: {e}") 



def get_state_geojson_path(): 
    PROJECT_DIR = Path().resolve() 
    DATA_DIR = PROJECT_DIR / "data" 
    # Ensure the data directory exists
    DATA_DIR.mkdir(exist_ok=True) 
    geojson_files = list(DATA_DIR.glob("*tracts.geojson"))
    states_available = sorted([f.name.split("_")[0].upper() for f in geojson_files])
    default_index = states_available.index("GA") if "GA" in states_available else 0 
    selected_state = st.sidebar.selectbox("Select State of Interest", states_available, index=default_index) 
    
    
    if states_available:
        return selected_state, f"data/{selected_state.lower()}_tracts.geojson" 
    else:
        st.sidebar.warning("No state GeoJSON files found in the data folder.") 
        return "GA", "data/ga_tracts.geojson" 

@st.cache_resource 
def get_cached_map(state_code, fips_prefix): 
    conn = psycopg2.connect(DB_CONN) 
    cur = conn.cursor() 
    m = initialize_map(cur, state_code, fips_prefix, view_selection) 
    cur.close() 
    conn.close() 
    return m

@st.cache_data 
def get_cached_shelters(state_code):
    cur = None
    conn = None
    try:
        conn = psycopg2.connect(DB_CONN) 
        cur = conn.cursor() 
        shelters_sql = read_sql_file(MAP_SHELTERS_STATE_FILE) 
        cur.execute(shelters_sql, (state_code,)) 
        rows = cur.fetchall() 
        cur.close() 
        conn.close()
        st.write("Rows returned by get_cached_shelters = ", len(rows))
        return rows 
    except Exception as e: 
        print(f"Error fetching shelters: {e}") 
        return []
    finally:
        if cur is not None: 
            cur.close() 
        if conn is not None: 
            conn.close()
        
    
@st.cache_data
def get_cached_clinics(fips_prefix):
    cur = None
    conn = None
    try:
        conn = psycopg2.connect(DB_CONN) 
        cur = conn.cursor() 
        clinics_sql = read_sql_file(MAP_CLINICS_STATE_FILE) 
        cur.execute(clinics_sql, (fips_prefix,)) 
        rows = cur.fetchall() 
        cur.close() 
        conn.close() 
        return rows 
    except Exception as e: 
        print(f"Error fetching tracts: {e}")
        return []
    finally:
        if cur is not None: 
            cur.close() 
        if conn is not None: 
            conn.close()
            
    
@st.cache_data 
def get_cached_map_center(fips_prefix):
    cur = None
    conn = None
    try:
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()
        center_sql = read_sql_file(MAP_CENTER_FILE)
        cur.execute(center_sql, (fips_prefix,)) 
        result = cur.fetchone() 
        cur.close() 
        conn.close() 
        if result and result[0] is not None:
            return result[0], result[1] 
        else: 
            return 33.7490, -84.3880 
    except Exception as e:
        print(f"Error calculating map center: {e}") 
        return 33.7490, -84.3880
    finally:
        if cur is not None: 
            cur.close() 
        if conn is not None: 
            conn.close()
    

@st.cache_data
def get_cached_geojson_data(fips_prefix): 
    cur = None
    conn = None
    try: 
        conn = psycopg2.connect(DB_CONN) 
        cur = conn.cursor() 
        tracts_sql = read_sql_file(MAP_TRACTS_STATE_FILE) 
        cur.execute(tracts_sql, (fips_prefix,)) 
        features = [] 
        for tract_id, density, geom_json in cur.fetchall():
            geom_dict = json.loads(geom_json)
            feature = { "type": "Feature", "geometry": geom_dict, "properties": { "tract_id": tract_id, "pet_density": int(density) } }
            features.append(feature) 
        cur.close() 
        conn.close() 
        return { "type": "FeatureCollection", "features": features } 
    except Exception as e: 
        print(f"Error fetching tracts: {e}") 
        return {"type": "FeatureCollection", "features": []}
    finally:
        if cur is not None: 
            cur.close() 
        if conn is not None: 
            conn.close()
   
def execute_pipeline(): 
    try: 
        # 1. Get the active state selection and file path from our dropdown helper 
        state_code, state_path = get_state_geojson_path() 
        # 2. Load our FIPS mapping dynamically right when we need it 
        fips_map = load_fips_map("state_fips_mapping.csv")
        fips_prefix = fips_map.get(state_code, "13") + "%"
        # 3. Connect to Postgres (Read-Only) 
        conn = psycopg2.connect(DB_CONN) 
        cur = conn.cursor() 
        # 4. Generate the map dynamically using the state-specific SQL queries
        m = initialize_map(state_code, fips_prefix, view_selection)
        
        
        
        get_cached_clinics(fips_prefix)
        get_cached_shelters(fips_prefix)
        cur.close() 
        conn.close() 
        # 5. Render the map in the Streamlit interface 
        #st_folium(m, width=1200, height=800)
        # folium_static is deprecated but it displays top right corner legend of highways, etc.
        folium_static(m, width=1200, height=800)
        
        # Add plotting and figuring outliers.
        with st.expander("Statistical Outliers and Pet Density Distribution"):
            display_outlier_analysis(fips_prefix, state_code)
        
        print("Web pipeline executed successfully.") 
    except Exception as e: st.error(f"Pipeline error: {e}") 
    


def initialize_map(state_code, fips_prefix, view_selection): 
    try:
        # 1. Get the cached map center (Calculated from database once)
        folium.Map(location=[33.7490, -84.3880], zoom_start=8)
        center_lat, center_lon = get_cached_map_center(fips_prefix)

        # Initialize map with tiles=None to allow custom named layers
        m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles=None)
        folium.TileLayer("openstreetmap", name="Highways and Roads").add_to(m)
        folium.TileLayer("cartodbpositron", name="Clean Gray").add_to(m)
        clinic_cluster = folium.FeatureGroup(name="Clinics").add_to(m)
        clinics_data = get_cached_clinics(state_code)
        # Choose clinic maps only if user clicks on Clinics Only or Both for radio buttons in sidebar.
        if view_selection in ["Both", "Clinics Only"]:
            for name, address, email, phone, lat, lon in clinics_data:
                directions_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                popup_html = f"<b>{name}</b><br><br>{address}<br><br>"
                
                if email and email.strip() != "":
                    popup_html += f"<a href='mailto:{email}'>Email Clinic</a><br><br>"
                if phone and phone.strip() != "":
                    popup_html += f"<a href='tel:{phone}'>Call: {phone}</a><br><br>"
                    
                popup_html += f"<a href='{directions_url}' target='_blank'>Get Directions</a>"
                
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_html,
                    icon=folium.Icon(color="red", icon="plus")
                ).add_to(clinic_cluster)
                
            # 3. Plot shelters using our cached list helper (inside the cluster layer)
        shelter_cluster = MarkerCluster(name="Shelters").add_to(m)
        shelters_data = get_cached_shelters(state_code)
        # Choose shelter maps only if user clicks on Shelters Only or Both for radio buttons in sidebar.
        if view_selection in ["Both", "Shelters Only"]:
            for name, address, email, phone, lat, lon in shelters_data:
                directions_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                popup_html = f"<b>{name}</b><br><br>{address}<br><br>"
                
                if email and email.strip() != "":
                    popup_html += f"<a href='mailto:{email}'>Email Shelter</a><br><br>"
                if phone and phone.strip() != "":
                    popup_html += f"<a href='tel:{phone}'>Call: {phone}</a><br><br>"
                    
                popup_html += f"<a href='{directions_url}' target='_blank'>Get Directions</a>"
                
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_html,
                    icon=folium.Icon(color="blue", icon="home")
                ).add_to(shelter_cluster)
         
               
        # 4. Add the census tracts and their tooltips
        add_census_tracts_to_map(m, fips_prefix)
          
        # 5. Add the layer control only once at the very end
        folium.LayerControl(collapsed=False).add_to(m)
        
        print("initialize_map executed successfully with state-specific layers.")
        return m
    except Exception as e:
        print(f"Error mapping locations: {e}")
        return folium.Map(location=[33.7490, -84.3880], zoom_start=8)

@st.cache_data 
def get_tract_densities_df(fips_prefix): 
    conn = None 
    cur = None 
    try: 
        conn = psycopg2.connect(DB_CONN) 
        cur = conn.cursor() 
        #query = "SELECT tract_id, pet_density FROM census_tracts WHERE tract_id LIKE %s;" 
        query = read_sql_file(OUTLIER_FILE)
        cur.execute(query, (fips_prefix,)) 
        rows = cur.fetchall() 
        return pd.DataFrame(rows, columns=["tract_id", "pet_density"])
    except Exception as e: 
        print(f"Error fetching densities for boxplot: {e}") 
        return pd.DataFrame(columns=["tract_id", "pet_density"]) 
    finally: 
        if cur is not None:
            cur.close() 
        if conn is not None: 
            conn.close() 
            
def display_outlier_analysis(fips_prefix, state_code):
    
    df = get_tract_densities_df(fips_prefix) 
    if df.empty or df["pet_density"].isnull().all(): 
        st.warning(f"No density data available for {state_code}.") 
        return 
    # Compute IQR and upper whisker threshold 
    # Take care of problem with Decimal and float incompatibility in psycopg2.
    df["pet_density"] = pd.to_numeric(df["pet_density"], errors="coerce")
    q1 = df["pet_density"].quantile(0.25) 
    #print(df["pet_density"].dtype)
    #print(df["pet_density"].map(type).value_counts())
    q3 = df["pet_density"].quantile(0.75)
    iqr = q3 - q1 
    whisker_limit = q3 + 1.5 * float(iqr)
    outliers_df = df[df["pet_density"] > whisker_limit].sort_values(by="pet_density", ascending=False)
    st.subheader(f"Statistical Outliers & Pet Density Distribution ({state_code})") 
     # Plot horizontal boxplot with Seaborn 
    sns.set_theme(style="whitegrid") 
    fig, ax = plt.subplots(figsize=(10, 2.5)) 
    sns.boxplot(y=df["pet_density"], color="#ff7f00", ax=ax) 
    ax.set_title(f"{state_code} Census Tracts: Pet Density Distribution") 
    ax.set_xlabel("Estimated Pets Per Tract") 
    st.pyplot(fig) 
    plt.close(fig) 
    st.write(f"Upper whisker cutoff: {int(whisker_limit)} estimated pets. Found {len(outliers_df)} outlier tracts.")
    if not outliers_df.empty:
        st.dataframe(outliers_df, use_container_width=True) 


if __name__ == "__main__":
    execute_pipeline()