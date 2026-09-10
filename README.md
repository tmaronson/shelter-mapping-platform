### Introduction
The _**Shelter Mapping Platform**_ is an open-source, data-driven initiative created through the 
_**Aronson Fund for Beasties and Humans**_. Its primary mission is to help animal rescues, 
philanthropic donors, and mobile veterinary clinics identify underserved communities 
and veterinary deserts across the United States. 
By combining US Census demographic data with national animal welfare registries, 
the platform highlights high-need neighborhoods where families lack access to affordable 
spay, neuter, and wellness services.

### Inspiration and Application Description
This project and application was a result of many things. Volunteering for animal organizations, having an extended pet family and fosters comprised much of the inspiration. Interest in philanthropy and starting the Donor Advised Fund ensures the mission is continued into the future. Contributing in many ways is critical knowing animals can be a victime of abuse, or euthanasia due to overcrowding in shelters. Taking a remote course on starting an animal sanctuary through Best Friends Animal Society in 2024 provided many ideas and facts in great detail. The last week in Kanab, Utah provided a way to meet the founders, directors of various services, staff, the animals, and others in the class personally.

### Project Description
Users can explore interactive state maps, inspect estimated pet density across 
color-coded census tract heatmaps to indicate census tracts, and view detailed contact information, 
phone links, and one-click **Google Maps** driving directions for over ten thousand shelters 
and sixteen thousand veterinary clinics. 
The platform also integrates statistical outlier diagnostics, 
calculating interquartile range thresholds to pinpoint priority candidate
areas for mobile clinic outreach. The Platform provides information for <ins>50 US states 
and the District of Columbia</ins>. On one tab the user can view shelters, clinics, or both and 
see a plain background or view a background with roads and highways.
On another tab maps are views of top outlier tracts where the distance to clinics is ranked. Users can
click on another area labeled across color-coded census tract heatmaps by tract to actually see that particular outlier tract highlighted on the map.

### High Level Technical Explanation
The application is built with **Streamlit** and deployed as a strictly read-only web service
on **Streamlit Community Cloud**. The backend is powered by a decoupled **PostgreSQL** and **PostGIS** 
database hosted on **Neon**, storing over eighty-four thousand census tract boundary MultiPolygons 
with spatial indexing. Geographic queries use **PostGIS** functions like `ST_SimplifyPreserveTopology` 
for fast payload transfers, while Folium provides interactive 
multi-layer visualization with dynamic basemaps. 
Statistical distributions and boxplots are computed using **Pandas** and **Seaborn**.

### Some Navigation Tips for the application:
* Start by selecting a state from the sidebar dropdown to load the local census tracts and pet density heatmap. 
* Use the top tabs to switch between the Interactive Map, the Outlier & Desert Analysis, or this present tab. 
* Hover over any tract when the Census Tracts checkbox is checked to see tract id and pet density.
* On the map, toggle layer checkboxes to isolate facilities or view the road network, and click any marker for direct *phone calls*, *email*, and one-click **Google Maps** *driving directions*. Please note all information is/was not available for all clinic and shelter markers.
* On the outlier tab, inspect the boxplot distribution and select an outlier tract to see its highlighted boundary on the map along with the five closest veterinary clinics and driving distances.
* If you see a green circle on the map with a number, this denotes a cluster of shelters or clinics. Click on the circle to see the number of shelters denoted by the number. The cluster is used to prevent additional clutter on the map.

