The _**Shelter Mapping Platform**_ is an open-source, data-driven initiative created through the 
_**Aronson Fund for Beasties and Humans**_. Its primary mission is to help animal rescues, 
philanthropic donors, and mobile veterinary clinics identify underserved communities 
and veterinary deserts across the United States. 
By combining US Census demographic data with national animal welfare registries, 
the platform highlights high-need neighborhoods where families lack access to affordable 
spay, neuter, and wellness services.

Users can explore interactive state maps, inspect estimated pet density across 
color-coded census tract heatmaps to indicate census tracts, and view detailed contact information, 
phone links, and one-click **Google Maps** driving directions for over ten thousand shelters 
and sixteen thousand veterinary clinics. 
The platform also integrates statistical outlier diagnostics, 
calculating interquartile range thresholds to pinpoint priority candidate
areas for mobile clinic outreach. The Platform provides information for <ins>50 US states 
and the District of Columbia</ins>. The user can view shelters, clinics, or both and 
see a plain background or view a background with roads and highways.
Below the maps are views of top outlier tracts where the distance to clinics is ranked. Users can
click on another area labeled across color-coded census tract heatmaps by tract to actually see that particular outlier tract highlighted on
the map.

The application is built with **Streamlit** and deployed as a strictly read-only web service
on **Streamlit Community Cloud**. The backend is powered by a decoupled **PostgreSQL** and **PostGIS** 
database hosted on **Neon**, storing over eighty-four thousand census tract boundary MultiPolygons 
with spatial indexing. Geographic queries use **PostGIS** functions like `ST_SimplifyPreserveTopology` 
for fast payload transfers, while Folium provides interactive 
multi-layer visualization with dynamic basemaps. 
Statistical distributions and boxplots are computed using **Pandas** and **Seaborn**.

### Some Navigation Tips for the application:

* Start by selecting a state from the sidebar dropdown to load the local census tracts and pet density heatmap. 
* Use the top tabs to switch between the Interactive Map and the Outlier & Desert Analysis. 
* On the map, toggle layer checkboxes to isolate facilities or view the road network, and click any marker for direct phone calls, email, and one-click **Google Maps** driving directions. 
* On the outlier tab, inspect the boxplot distribution and select an outlier tract to see its highlighted boundary on the map along with the five closest veterinary clinics and driving distances.

