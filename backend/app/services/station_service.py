from pathlib import Path
from haversine import haversine
import pandas as pd

class StationService:
    def __init__(self):
        base_dir=Path(__file__).resolve().parent.parent.parent.parent
        station_path=base_dir/"data"/"stations"/"stations.csv"
        self.stations=pd.read_csv(station_path)

    def get_nearest_station(self, user_lat:float, user_lon:float):
        nearest_station=None
        min_distance=float("inf")

        for _,row in self.stations.iterrows():
            station_location=(
                row["latitude"],
                row["longitude"]
            )
            user_location=(user_lat, user_lon)
            distance=haversine(user_location, station_location)
            if distance<min_distance:
                min_distance=distance
                nearest_station=row

        return {
            "station":nearest_station["station"],
            "station_encoded":int(nearest_station["station_encoded"]),
            "latitude":float(nearest_station["latitude"]),
            "longitude":float(nearest_station["longitude"]),
            "distance_km":round(min_distance, 2)
        }

station_service=StationService()