# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import requests
import folium
import math
from folium import FeatureGroup, Marker, LayerControl
from newsapi import NewsApiClient


def api(request):
    
    # Get request from NASA's EONET
    days = "50"
    response = requests.get(
        "https://eonet.gsfc.nasa.gov/api/v3/events?years=" + days
    ).json()
    if response:
          print("success")

          # setup folium map
          m = folium.Map(width="100%", height="100%", location=(0, 0), max_bounds=True)

          # sort response by category
          events = response["events"]  # .sort(key=lambda e:e['categories'][0]['title'])
          events.sort(key=lambda e: e["categories"][0]["title"])

          mySet = set()
          # sets first category
          group = FeatureGroup(events[0]["categories"][0]["title"])

          for i in events:

               title = str(i["title"])
               category = str(i["categories"][0]["title"])

               if len(i["geometry"]) > 1:

                    # Multiple coordinated event i.e. storm
                    coord_list = []
                    date_range = (
                    i["geometry"][0]["date"][:10]
                    + " to "
                    + i["geometry"][len(i["geometry"]) - 1]["date"][:10]
                    )
                    rotate = triangle_rotation(
                    i["geometry"][len(i["geometry"]) - 2]["coordinates"],
                    i["geometry"][len(i["geometry"]) - 1]["coordinates"],
                    ) - 270

                    # iterate through geometry array that contains wanted coordinates
                    counter = 1
                    for j in i["geometry"]:
                         if "Tiffany" in title:
                              print(j["date"])
                         coordinates = j["coordinates"]
                         # fix nasa's coordinates to match folium
                         coordinates.reverse()
                         #test

                         coord_list.append(coordinates)

                    print("break")

                    # featuregroup
                    if category in mySet:
                         folium.PolyLine(
                         coord_list,
                         color="green",
                         popup=(title, date_range),
                         tooltip=title,
                         ).add_to(group)
                         folium.RegularPolygonMarker(
                         location=i["geometry"][len(i["geometry"]) - 1]["coordinates"],
                         fill_color="green",
                         icon=folium.Icon(icon='chevron-up', prefix='fa'),
                         color="green",
                         number_of_sides=3,
                         radius=6,
                         rotation=rotate ,
                         popup=(title, date_range),
                         tooltip=title,
                         ).add_to(group)

                         group.add_to(m)

                    else:

                         group = folium.FeatureGroup(category)
                         mySet.add(category)

                         folium.PolyLine(
                         coord_list,
                         color="green",
                         popup=(title, date_range),
                         tooltip=title,
                         ).add_to(group)
                         folium.RegularPolygonMarker(
                         location=i["geometry"][len(i["geometry"]) - 1]["coordinates"],
                         fill_color="green",
                         color="green",
                         number_of_sides=3,
                         radius=6,
                         rotation=rotate, 
                         popup=(title, date_range),
                         tooltip=title,
                         ).add_to(group)

                         group.add_to(m)

               else:
                    # single coordinated event

                    date = i["geometry"][0]["date"][:10]
                    coord_list = i["geometry"][0]["coordinates"]

                    # fix nasa's coordinates to match folium
                    coord_list.reverse()

                    
                    icon = folium.Icon(icon='fire',color='blue',prefix='fa')
                    
                    
                    # feature test

                    if category in mySet:
                         

                         folium.Marker(
                         coord_list, popup=(title, date), tooltip=title, icon=icon
                         ).add_to(group)

                         group.add_to(m)

                    else:

                         group = folium.FeatureGroup(category)

                         mySet.add(category)

                         

                         folium.Marker(
                         coord_list, popup=(title, date), tooltip=title, icon=icon
                         ).add_to(group)

                         group.add_to(m)

          folium.LayerControl().add_to(m)

          m.fit_bounds([(-80, -170), (80, 170)])
          # Needed for folium to display on html
          m = m._repr_html_()

          context = {
                "events": response["events"],
                "myMap": m,
          }

          return render(request, "api/api.html", context)










def triangle_rotation(coord1, coord2):
    # calculates the degree of which the triangle should be pointing
    # using atan2(y2-y1,x2-x1) 0:y 1:x
    print(coord1)
    print(coord2)
    res = math.atan2(coord1[0] - coord2[0], coord1[1] - coord2[1])*100
    return res


