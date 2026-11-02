
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from psycopg2.extras import RealDictCursor

from app.database.connection import get_database_connection


def get_station_historical_analytics(station_id):
    """
    Fetch the last 30 days of hourly air quality data
    for a particular station.
    """

    ist = ZoneInfo("Asia/Kolkata")

    # Database timestamps are stored as IST without timezone information.
    cutoff_time = (
        datetime.now(ist) - timedelta(days=30)
    ).replace(tzinfo=None)

    query = """
        SELECT DISTINCT ON (DATE_TRUNC('hour', timestamp))
            id,
            station_id,
            station_name,
            latitude,
            longitude,
            timestamp,
            aqi,
            aqi_category,
            pm25,
            pm10,
            no2,
            so2,
            co,
            o3
        FROM public.air_quality_data
        WHERE station_id = %s
          AND timestamp >= %s
        ORDER BY
            DATE_TRUNC('hour', timestamp) ASC,
            timestamp DESC,
            id DESC;
    """

    connection = None

    try:
        connection = get_database_connection()

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (station_id, cutoff_time))
            records = cursor.fetchall()

        data = []

        for record in records:
            data.append({
                "timestamp": record["timestamp"],
                "aqi": record["aqi"],
                "aqi_category": record["aqi_category"],
                "pm25": record["pm25"],
                "pm10": record["pm10"],
                "no2": record["no2"],
                "so2": record["so2"],
                "co": record["co"],
                "o3": record["o3"]
            })

        station_name = records[0]["station_name"] if records else None

        return {
            "station_id": station_id,
            "station_name": station_name,
            "period": "30_days",
            "interval": "1_hour",
            "timezone": "Asia/Kolkata",
            "total_records": len(data),
            "available_pollutants": [
                "aqi", "pm25", "pm10",
                "no2", "so2", "co", "o3"
            ],
            "data": data
        }

    finally:
        if connection:
            connection.close()
