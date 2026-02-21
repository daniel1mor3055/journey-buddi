# Maps & Routing Integration

## Overview

Maps and routing are central to Journey Buddi's user experience and backend logic. The frontend renders interactive maps showing itinerary routes, points of interest, and real-time traveler position. The backend computes drive times, distances, and route geometry to optimize daily schedules and suggest efficient activity ordering. This document specifies the providers, integration approach, and NZ-specific considerations.

## Frontend Maps: Mapbox GL JS

### Why Mapbox Over Google Maps

| Factor | Mapbox | Google Maps |
|--------|--------|-------------|
| **Customization** | Full style control via Mapbox Studio, custom layers, 3D terrain | Limited style customization |
| **Pricing** | 50K free map loads/mo, 100K free direction requests/mo | $200/mo credit, then $7 per 1,000 loads |
| **Cost at scale** | Predictable, lower at moderate scale | Expensive at scale |
| **Offline tiles** | Supported (mobile SDK) | Limited offline support |
| **Open data** | Built on OpenStreetMap | Proprietary data |
| **3D terrain** | Native 3D terrain with hillshading | Flat unless using Earth API |
| **Route visualization** | Animated route lines, gradient coloring | Standard polylines |
| **Developer experience** | Excellent React bindings, declarative API | Imperative API, wrapper needed |

For an adventure travel app that needs beautiful, immersive map experiences with mountain terrain, custom markers for activities, and animated route paths, Mapbox is the clear choice.

### Mapbox Integration Points

| Feature | Mapbox Product | Use Case |
|---------|---------------|----------|
| Base map display | Mapbox GL JS | Interactive trip map |
| 3D terrain | Mapbox Terrain-RGB | Mountain/hiking visualization |
| Route lines | GeoJSON LineString layers | Show driving/hiking routes |
| Activity markers | Custom markers with popups | Show activities on map |
| Geocoding | Mapbox Geocoding API | Location search bar |
| Directions | Mapbox Directions API | Drive time/route calculations |
| Static images | Mapbox Static Images API | Map thumbnails for sharing |

### Frontend Implementation

```typescript
import mapboxgl from 'mapbox-gl';
import { useEffect, useRef } from 'react';

interface TripMapProps {
  itinerary: ItineraryDay[];
  currentLocation?: [number, number];
}

export function TripMap({ itinerary, currentLocation }: TripMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/journeybuddi/custom-adventure',
      center: [172.0, -43.5],  // NZ center
      zoom: 6,
      pitch: 45,               // 3D perspective
      terrain: { source: 'mapbox-dem', exaggeration: 1.2 },
    });

    map.current.on('load', () => {
      addTerrainSource(map.current!);
      addRouteLayer(map.current!, itinerary);
      addActivityMarkers(map.current!, itinerary);
    });

    return () => map.current?.remove();
  }, []);

  return <div ref={mapContainer} className="w-full h-[60vh] rounded-xl" />;
}

function addTerrainSource(map: mapboxgl.Map) {
  map.addSource('mapbox-dem', {
    type: 'raster-dem',
    url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
    tileSize: 512,
    maxzoom: 14,
  });
  map.addLayer({
    id: 'hillshading',
    source: 'mapbox-dem',
    type: 'hillshade',
  });
}

function addRouteLayer(map: mapboxgl.Map, itinerary: ItineraryDay[]) {
  const routeGeoJSON = itineraryToGeoJSON(itinerary);
  map.addSource('route', { type: 'geojson', data: routeGeoJSON });
  map.addLayer({
    id: 'route-line',
    type: 'line',
    source: 'route',
    layout: { 'line-join': 'round', 'line-cap': 'round' },
    paint: {
      'line-color': '#3b82f6',
      'line-width': 4,
      'line-opacity': 0.8,
    },
  });
}
```

### Custom Map Style

Journey Buddi uses a custom Mapbox Studio style that:
- Emphasizes natural features (mountains, rivers, coastline)
- Uses warm, adventure-themed color palette
- Shows hiking trails and DOC hut locations (from OpenStreetMap data)
- Reduces urban clutter for non-urban trips
- Includes custom icons for activity types (hiking, kayaking, wildlife, etc.)

## Routing Engine: Mapbox Directions API

### Endpoint

```
GET https://api.mapbox.com/directions/v5/mapbox/{profile}/{coordinates}
  ?geometries=geojson
  &overview=full
  &steps=true
  &access_token={MAPBOX_TOKEN}
```

### Profiles

| Profile | Use Case |
|---------|----------|
| `driving` | Car/campervan travel between locations |
| `driving-traffic` | Drive times accounting for live traffic |
| `walking` | Short walks between nearby activities |
| `cycling` | Cycle trail planning (future) |

### What We Calculate

| Output | API Field | Use Case |
|--------|-----------|----------|
| Total drive time | `routes[0].duration` (seconds) | Schedule optimization, departure time |
| Distance | `routes[0].distance` (meters) | Display to user, fuel estimates |
| Route geometry | `routes[0].geometry` (GeoJSON) | Display route on map |
| Turn-by-turn steps | `routes[0].legs[0].steps[]` | Detailed directions (future) |
| Via waypoints | Multi-point routes | Scenic stops along the way |

### Multi-Stop Route Optimization

For a day with multiple activities, the system determines the optimal visit order:

```python
import httpx

class MapboxRouter:
    BASE_URL = "https://api.mapbox.com/directions/v5/mapbox"

    def __init__(self, access_token: str):
        self.token = access_token
        self.client = httpx.AsyncClient(timeout=15.0)

    async def get_route(
        self,
        waypoints: list[tuple[float, float]],
        profile: str = "driving",
    ) -> RouteResult:
        coords = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
        url = f"{self.BASE_URL}/{profile}/{coords}"
        params = {
            "geometries": "geojson",
            "overview": "full",
            "steps": "true",
            "access_token": self.token,
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        route = data["routes"][0]

        return RouteResult(
            duration_seconds=route["duration"],
            duration_minutes=round(route["duration"] / 60),
            distance_km=round(route["distance"] / 1000, 1),
            geometry=route["geometry"],
            legs=[
                RouteLeg(
                    duration_minutes=round(leg["duration"] / 60),
                    distance_km=round(leg["distance"] / 1000, 1),
                )
                for leg in route["legs"]
            ],
        )

    async def optimize_stop_order(
        self,
        origin: tuple[float, float],
        stops: list[tuple[float, float]],
        destination: tuple[float, float],
    ) -> list[int]:
        """Use Mapbox Optimization API to find best visit order."""
        all_points = [origin] + stops + [destination]
        coords = ";".join(f"{lon},{lat}" for lat, lon in all_points)

        url = f"https://api.mapbox.com/optimized-trips/v1/mapbox/driving/{coords}"
        params = {
            "source": "first",
            "destination": "last",
            "roundtrip": "false",
            "access_token": self.token,
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        optimized_order = [wp["waypoint_index"] for wp in data["waypoints"]]
        return optimized_order[1:-1]  # exclude origin and destination
```

### Scenic Route Options

For adventure travelers, the fastest route isn't always the best. Journey Buddi can suggest scenic alternatives:

```python
async def get_scenic_alternative(
    self,
    origin: tuple[float, float],
    destination: tuple[float, float],
) -> dict:
    """Fetch both fastest and scenic (avoid highways) routes."""
    fastest = await self.get_route([origin, destination], profile="driving")

    scenic = await self.get_route(
        [origin, destination],
        profile="driving",
        # Mapbox allows exclude=motorway for scenic routing
    )

    time_difference = scenic.duration_minutes - fastest.duration_minutes
    return {
        "fastest": fastest,
        "scenic": scenic,
        "extra_time_minutes": time_difference,
        "suggestion": (
            f"The scenic route adds {time_difference} minutes but follows "
            f"the coast through stunning countryside."
            if time_difference < 45
            else None
        ),
    }
```

### Pricing

| Product | Free Tier | Over-Free Cost |
|---------|-----------|---------------|
| Directions API | 100,000 requests/mo | $0.50 per 1,000 |
| Optimization API | 100,000 requests/mo | $1.00 per 1,000 |
| Map loads (web) | 50,000/mo | $5.00 per 1,000 |
| Geocoding | 100,000 requests/mo | $0.75 per 1,000 |
| Static Images | 25,000/mo | $2.00 per 1,000 |

At MVP scale (50 active trips), all usage fits within free tiers.

## Fallback Routing: OSRM (Open Source Routing Machine)

### Why OSRM as Fallback

- Fully open-source, can be self-hosted
- Uses OpenStreetMap data
- No API key, no rate limits, no cost
- Excellent for basic point-to-point routing
- Supports driving, walking, and cycling profiles

### Endpoint (Public Demo Server)

```
GET https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}
  ?overview=full
  &geometries=geojson
  &steps=true
```

### Self-Hosted Option

For production fallback, OSRM can be self-hosted with NZ-specific OpenStreetMap data:

```bash
# Download NZ OSM data
wget https://download.geofabrik.de/australia-oceania/new-zealand-latest.osm.pbf

# Extract and prepare routing graph
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend \
  osrm-extract -p /opt/car.lua /data/new-zealand-latest.osm.pbf

docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend \
  osrm-partition /data/new-zealand-latest.osrm

docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend \
  osrm-customize /data/new-zealand-latest.osrm

# Run routing server
docker run -t -p 5000:5000 -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend \
  osrm-routed --algorithm mld /data/new-zealand-latest.osrm
```

### Limitations vs Mapbox

| Feature | Mapbox Directions | OSRM |
|---------|-------------------|------|
| Live traffic | Yes (driving-traffic profile) | No |
| Route optimization (TSP) | Yes (Optimization API) | No (need separate solver) |
| Scenic routing | Partial (exclude motorway) | No |
| Turn-by-turn voice | Yes | Basic |
| Elevation-aware routing | No | No |
| Cost | Free tier, then paid | Free (self-hosted) |

## POI Discovery

### Primary: Overpass API (OpenStreetMap)

Overpass queries OpenStreetMap's full dataset. Excellent for discovering hiking trails, viewpoints, campsites, DOC huts, and natural features.

```
POST https://overpass-api.de/api/interpreter
```

#### Example Queries

**Find viewpoints near a location:**
```
[out:json];
node
  ["tourism"="viewpoint"]
  (around:10000, -44.0, 168.7);
out body;
```

**Find DOC huts in a region:**
```
[out:json];
node
  ["tourism"="alpine_hut"]
  ["operator"~"Department of Conservation|DOC"]
  (-46.0, 166.0, -44.0, 170.0);
out body;
```

**Find waterfalls:**
```
[out:json];
node
  ["waterway"="waterfall"]
  (around:50000, -44.5, 168.0);
out body;
```

**Find fuel stations (for campervan planning):**
```
[out:json];
node
  ["amenity"="fuel"]
  (around:30000, -45.0, 168.7);
out body;
```

### POI Normalization

```python
class PointOfInterest(BaseModel):
    osm_id: int
    name: str
    category: str                  # "viewpoint", "hut", "campsite", "fuel", etc.
    lat: float
    lon: float
    tags: dict[str, str]           # raw OSM tags
    elevation_m: Optional[float]
    opening_hours: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    fee: Optional[str]
    wheelchair: Optional[str]

class OverpassAdapter:
    BASE_URL = "https://overpass-api.de/api/interpreter"

    async def search_pois(
        self, lat: float, lon: float, radius_m: int, category: str
    ) -> list[PointOfInterest]:
        query = self._build_query(lat, lon, radius_m, category)
        response = await self.client.post(self.BASE_URL, data={"data": query})
        response.raise_for_status()
        data = response.json()

        return [
            PointOfInterest(
                osm_id=el["id"],
                name=el.get("tags", {}).get("name", "Unnamed"),
                category=category,
                lat=el["lat"],
                lon=el["lon"],
                tags=el.get("tags", {}),
                elevation_m=el.get("tags", {}).get("ele"),
                opening_hours=el.get("tags", {}).get("opening_hours"),
                website=el.get("tags", {}).get("website"),
                phone=el.get("tags", {}).get("phone"),
                fee=el.get("tags", {}).get("fee"),
                wheelchair=el.get("tags", {}).get("wheelchair"),
            )
            for el in data.get("elements", [])
            if el["type"] == "node"
        ]

    def _build_query(self, lat: float, lon: float, radius: int, category: str) -> str:
        tag_map = {
            "viewpoint": '["tourism"="viewpoint"]',
            "campsite": '["tourism"="camp_site"]',
            "hut": '["tourism"="alpine_hut"]',
            "waterfall": '["waterway"="waterfall"]',
            "fuel": '["amenity"="fuel"]',
            "parking": '["amenity"="parking"]',
            "toilet": '["amenity"="toilets"]',
            "info_center": '["tourism"="information"]["information"="office"]',
        }
        tag = tag_map.get(category, f'["tourism"="{category}"]')
        return f'[out:json];node{tag}(around:{radius},{lat},{lon});out body;'
```

### Enhancement: Google Places API

Used sparingly (expensive) to enrich POI data with:
- Professional photos
- User reviews and ratings
- Current opening hours (more reliable than OSM)
- Place popularity / busy times

```python
class GooglePlacesEnricher:
    async def enrich_poi(self, poi: PointOfInterest) -> PointOfInterest:
        """Enrich a POI with Google Places data. Use sparingly — $0.032/request."""
        result = await self._nearby_search(poi.lat, poi.lon, poi.name)
        if result:
            poi.google_rating = result.get("rating")
            poi.google_photo_ref = result.get("photos", [{}])[0].get("photo_reference")
            poi.google_place_id = result.get("place_id")
        return poi
```

## Geocoding

### Mapbox Geocoding API

Used for the location search bar in the app — when users type a destination name, it resolves to coordinates.

```
GET https://api.mapbox.com/geocoding/v5/mapbox.places/{search_text}.json
  ?country=nz                    # bias to NZ for pilot
  &types=place,poi,address
  &limit=5
  &access_token={TOKEN}
```

### Reverse Geocoding

Convert coordinates to a human-readable place name (for "You are near..."):

```
GET https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json
  ?types=place,locality
  &access_token={TOKEN}
```

## Elevation Data

### Purpose

For hiking activities, display the elevation profile of the trail so travelers can gauge difficulty.

### Source: Mapbox Terrain Tiles

Mapbox provides elevation data through raster-dem tiles. On the frontend, elevation profiles are rendered by sampling the terrain along a route's geometry.

### Alternative: Open-Elevation API

```
POST https://api.open-elevation.com/api/v1/lookup
Content-Type: application/json

{
  "locations": [
    {"latitude": -43.5946, "longitude": 170.1418},
    {"latitude": -43.5950, "longitude": 170.1420}
  ]
}
```

### Elevation Profile Rendering

```typescript
async function getElevationProfile(
  routeGeometry: GeoJSON.LineString,
  numSamples: number = 100
): Promise<ElevationPoint[]> {
  const coords = routeGeometry.coordinates;
  const totalDistance = calculateTotalDistance(coords);
  const sampleInterval = totalDistance / numSamples;

  const samplePoints = interpolateAlongLine(coords, sampleInterval);
  const elevations = await fetchElevations(samplePoints);

  return samplePoints.map((point, i) => ({
    distance_km: (sampleInterval * i) / 1000,
    elevation_m: elevations[i],
    lat: point[1],
    lon: point[0],
  }));
}
```

## NZ-Specific Road Data Considerations

### Road Types

| Road Type | Characteristics | Planning Impact |
|-----------|----------------|-----------------|
| State Highways (SH) | Main inter-city routes, well maintained | Reliable drive times, fuel available |
| Scenic Routes | Designated scenic drives, slower | Factor extra time, worth the detour |
| Gravel/Unsealed roads | Common in rural NZ, some iconic routes | Slower speeds, rental car restrictions |
| One-lane bridges | Very common in South Island | Minor delays, add buffer time |
| Mountain passes | Milford Road, Arthur's Pass, Lewis Pass | Weather-dependent, may close in winter |

### Campervan-Specific Routing

Many Journey Buddi users will be in campervans. Routing considerations:
- **Height restrictions**: Some tunnels and overpasses restrict vehicles >3.5m
- **Weight restrictions**: Some bridges have weight limits
- **Freedom camping spots**: Legal overnight parking locations
- **Dump station locations**: For campervan waste disposal
- **Narrower roads**: Some roads are unsuitable for large campervans

### Road Closure Integration

NZ Transport Agency (NZTA) provides road closure data:

```
GET https://www.journeys.nzta.govt.nz/api/highway-conditions
```

This feeds into the condition monitoring system. If a road on today's route is closed, the system alerts the user and suggests an alternative.

## Offline Map Strategy (Future)

For areas with poor cell coverage (common in NZ backcountry):

1. **Pre-download tiles**: Using Mapbox's offline tile packs, pre-download map tiles for the trip's region.
2. **Cached routes**: Store pre-computed route geometries and directions locally.
3. **Offline POI data**: Bundle key POI data (DOC huts, campsites, fuel stations) for offline access.
4. **Sync on reconnect**: When connectivity returns, sync any offline interactions and refresh data.

This is a future feature targeting the mobile app (PWA or native).

## Caching Strategy

| Data Type | Redis TTL | Rationale |
|-----------|-----------|-----------|
| Route (point-to-point) | 24 hours | Road conditions change daily |
| Optimized multi-stop | 12 hours | Recompute when activities change |
| POI search results | 7 days | POIs don't change frequently |
| Geocoding results | 30 days | Place names are stable |
| Elevation data | 30 days | Terrain doesn't change |

### Cache Key Structure

```
route:{profile}:{origin_hash}:{destination_hash}
poi:{category}:{lat_rounded}:{lon_rounded}:{radius}
geocode:{search_text_hash}
```

## Cross-References

- **Map display in UX**: See [Screen Flows](../04-ux/SCREEN-FLOWS.md)
- **Drive time in itinerary optimization**: See [Itinerary Generation](../02-product/ITINERARY-GENERATION.md)
- **Transport segments data model**: See [Data Model](../05-architecture/DATA-MODEL.md)
- **Tech stack (Mapbox choice)**: See [Tech Stack](../05-architecture/TECH-STACK.md)
- **Road closures in condition monitoring**: See [Condition Monitoring](../02-product/CONDITION-MONITORING.md)
