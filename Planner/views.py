from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import random
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from urllib.parse import quote
import logging
from datetime import datetime, timedelta

# Import your models
from Hotel.models import Hotels, Room
from Cabs.models import Cab, Vehicle

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GOOGLE_MAPS_KEYS = {
    "geocode": "AIzaSyBGX6KP8c1L_zrzRTysUU-rEiJlyiXBfmU",
    "places": "AIzaSyAp3MFgPLLIvizsUTiwAI3Jvyw8jd-G_kU",
    "directions": "AIzaSyBGX6KP8c1L_zrzRTysUU-rEiJlyiXBfmU"
}

class TravelPlanAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        logger.debug(f"Received request data: {data}")
        start = data.get("start")
        end = data.get("end")
        days = int(data.get("days", 3))
        budget = data.get("budget", "5000-7000")
        dates = data.get("dates", [])
        people = data.get("people", {"adults": 0, "children": 0, "infants": 0})

        if not start or not end:
            logger.error("Missing start or end location")
            return Response({"error": "Start and end locations are required."}, status=400)

        # Handle single-date input for multi-day trips
        if len(dates) == 1 and days > 1:
            start_date = datetime.strptime(dates[0], "%Y-%m-%d")
            dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
            logger.debug(f"Expanded dates: {dates}")

        cache_key = f"plans::{start}::{end}::{days}::{budget}"
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Returning cached plans for key: {cache_key}")
            return Response(cached)

        try:
            start_coords = self.geocode_location(start)
            end_coords = self.geocode_location(end)
            mid_coords = self.midpoint(start_coords, end_coords)

            # Increase radius and reduce min attractions for same start/end
            radius_km = 50 if start.lower() == end.lower() else 30
            min_attractions = 3 if start.lower() == end.lower() else 5
            attractions = self.get_attractions_along_route(start_coords, end_coords, num_points=4, radius_km=radius_km)

            if len(attractions) < min_attractions:
                logger.warning(f"Only {len(attractions)} attractions found, need at least {min_attractions}")
                raise Exception(f"Not enough attractions found (got {len(attractions)}, need {min_attractions}).")

            plans = []
            used_combinations = set()
            attempts = 0
            max_attempts = 20

            tier = self.get_tier(budget)

            while len(plans) < 5 and attempts < max_attempts:
                sample_stops = random.sample(attractions, min(len(attractions), 3))
                combo = tuple(sorted([stop["place_id"] for stop in sample_stops]))
                if combo not in used_combinations:
                    used_combinations.add(combo)
                    try:
                        directions = self.get_directions(start, end, sample_stops)
                        
                        plan = {
                            "start": start,
                            "end": end,
                            "stops": sample_stops,
                            "distance_km": directions["distance"],
                            "duration_hr": directions["duration"],
                            "map_url": directions["map_url"],
                            "dates": dates,
                            "people": people,
                            "tier": tier,
                        }

                        # Fetch ALL verified hotels (no budget filter for testing)
                        hotels_qs = Hotels.objects.filter(
                            is_verified=True,
                            is_active=True
                        )[:10]
                        
                        plan["hotels"] = [
                            {
                                "name": hotel.name,
                                "address": hotel.address,
                                "description": hotel.description,
                                "facilities": hotel.facilities.split(',') if hotel.facilities else [],
                                "main_image": hotel.main_image.url if hotel.main_image else "https://via.placeholder.com/400x300?text=Hotel+Image",
                                "contact_email": hotel.contact_email,
                                "contact_phone": hotel.contact_phone,
                                "location": hotel.location,
                                "room_prices": [float(room.price) for room in hotel.rooms.all()]  # For debugging
                            }
                            for hotel in hotels_qs
                        ]

                        # Fetch ALL verified cabs (no tier filter for testing)
                        cabs_qs = Cab.objects.filter(
                            is_verified=True,
                            is_active=True
                        )[:10]
                        
                        plan["cabs"] = [
                            {
                                "name": f"{cab.vehicle.brand} {cab.vehicle.model}" if cab.vehicle else "Unknown Cab",
                                "photo_url": cab.vehicle.vehicle_image.url if cab.vehicle and cab.vehicle.vehicle_image else "https://via.placeholder.com/400x300?text=Cab+Image",
                                "price_per_km": float(cab.price_per_km),
                                "tier": tier,
                                "rating": float(cab.rating),
                                "driver_name": cab.driver.name if cab.driver else None,
                                "base_fare": float(cab.base_fare),
                                "location": cab.location,
                            }
                            for cab in cabs_qs
                        ]
                        
                        plans.append(plan)
                    except Exception as e:
                        logger.warning(f"Skipping stop combination due to error: {str(e)}")
                attempts += 1

            if not plans:
                logger.error("No valid plans generated after max attempts")
                raise Exception("Could not generate any valid travel plans.")

            cache.set(cache_key, plans, timeout=60 * 60 * 3)
            logger.debug(f"Generated {len(plans)} plans, cached with key: {cache_key}")
            return Response(plans)

        except Exception as e:
            logger.error(f"Error generating plans: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)

    def get_tier(self, budget):
        try:
            low, high = map(int, budget.split("-"))
            if low >= 15000:
                return "luxury"
            elif low >= 7000:
                return "premium"
            else:
                return "standard"
        except:
            return "standard"

    def geocode_location(self, location):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": location, "key": GOOGLE_MAPS_KEYS["geocode"]}
        try:
            res = requests.get(url, params=params).json()
            if res.get("status") != "OK" or not res.get("results"):
                logger.error(f"Geocode failed for {location}: {res.get('status')}")
                raise Exception(f"Geocode failed for {location}: {res.get('status')}")
            loc = res["results"][0]["geometry"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"]}
        except Exception as e:
            logger.error(f"Geocode request failed: {str(e)}", exc_info=True)
            raise

    def midpoint(self, coord1, coord2):
        return {
            "lat": (coord1["lat"] + coord2["lat"]) / 2,
            "lng": (coord1["lng"] + coord2["lng"]) / 2
        }

    def get_attractions_along_route(self, start_coords, end_coords, num_points=4, radius_km=30):
        points = (
            [start_coords] if start_coords["lat"] == end_coords["lat"] and start_coords["lng"] == end_coords["lng"]
            else self.split_line(start_coords, end_coords, num_points)
        )
        all_attractions = []

        for point in points:
            attractions = self.get_nearby_attractions(point, radius_km=radius_km)
            all_attractions.extend(attractions)

        seen = set()
        unique = []
        for attr in all_attractions:
            if attr["place_id"] not in seen:
                seen.add(attr["place_id"])
                unique.append(attr)

        return sorted(unique, key=lambda p: p.get("rating", 0), reverse=True)[:15]

    def split_line(self, start, end, n):
        return [
            {
                "lat": start["lat"] + (end["lat"] - start["lat"]) * i / (n + 1),
                "lng": start["lng"] + (end["lng"] - start["lng"]) * i / (n + 1)
            }
            for i in range(1, n + 1)
        ]

    def get_nearby_attractions(self, location, radius_km=30):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{location['lat']},{location['lng']}",
            "radius": radius_km * 1000,
            "type": "tourist_attraction",
            "key": GOOGLE_MAPS_KEYS["places"]
        }
        try:
            res = requests.get(url, params=params).json()
            if res.get("status") != "OK":
                logger.error(f"Places API error: {res.get('status')} - {res.get('error_message', '')}")
                raise Exception(f"Google Places API Error: {res.get('status')}")
            results = res.get("results", [])
            if not results:
                logger.warning(f"No attractions found for location: {location}")
                return []

            places = []
            for place in results:
                geometry = place.get("geometry", {})
                loc = geometry.get("location", {})
                photos = place.get("photos", [])
                photo_url = (
                    f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photos[0]['photo_reference']}&key={GOOGLE_MAPS_KEYS['places']}"
                    if photos else "https://via.placeholder.com/400x300?text=Attraction+Image"
                )
                if "lat" in loc and "lng" in loc:
                    places.append({
                        "name": place.get("name", "Unknown Attraction"),
                        "vicinity": place.get("vicinity", "Unknown Location"),
                        "lat": loc["lat"],
                        "lng": loc["lng"],
                        "place_id": place.get("place_id"),
                        "rating": place.get("rating", 4.0),
                        "photo_url": photo_url,
                    })

            return sorted(places, key=lambda p: p.get("rating", 0), reverse=True)[:3]
        except Exception as e:
            logger.error(f"Places API request failed: {str(e)}", exc_info=True)
            raise

    def get_directions(self, start, end, stops):
        waypoints = "|".join([f"place_id:{stop['place_id']}" for stop in stops])
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": start,
            "destination": end,
            "waypoints": f"optimize:true|{waypoints}" if waypoints else "",
            "key": GOOGLE_MAPS_KEYS["directions"]
        }
        try:
            res = requests.get(url, params=params).json()
            if res.get("status") != "OK":
                logger.error(f"Directions API error: {res.get('status')} - {res.get('error_message', '')}")
                raise Exception(f"Directions API error: {res.get('status')}")
            routes = res.get("routes", [])
            if not routes:
                logger.error("No routes found in Directions API response")
                raise Exception("No routes found")
            route = routes[0]
            legs = route["legs"]
            total_km = sum([leg["distance"]["value"] for leg in legs]) / 1000
            total_hr = sum([leg["duration"]["value"] for leg in legs]) / 3600
            sanitized_waypoints = "|".join([quote(stop["name"]) for stop in stops])
            map_url = f"https://www.google.com/maps/dir/?api=1&origin={quote(start)}&destination={quote(end)}&waypoints={sanitized_waypoints}"
            return {
                "distance": round(total_km, 2),
                "duration": round(total_hr, 2),
                "map_url": map_url
            }
        except Exception as e:
            logger.error(f"Directions API request failed for waypoints {waypoints}: {str(e)}", exc_info=True)
            raise