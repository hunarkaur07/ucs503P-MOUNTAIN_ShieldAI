from sqlalchemy.orm import Session
from sqlalchemy import text


# =========================
# USERS IN RADIUS
# =========================

def get_users_in_radius(
    db: Session,
    lat: float,
    lon: float,
    radius_km: int = 20
):
    """
    Get users within a specified radius using PostGIS.
    """

    query = text("""
        SELECT
            id,
            name,
            ST_X(location::geometry) AS lon,
            ST_Y(location::geometry) AS lat
        FROM users
        WHERE
            location IS NOT NULL
            AND ST_DWithin(
                location::geography,
                ST_SetSRID(
                    ST_MakePoint(:lon, :lat),
                    4326
                )::geography,
                :radius_meters
            )
    """)

    result = db.execute(
        query,
        {
            "lat": lat,
            "lon": lon,
            "radius_meters": radius_km * 1000
        }
    ).fetchall()

    return result


# =========================
# REPORTS IN RADIUS
# =========================

def get_reports_in_radius(
    db: Session,
    lat: float,
    lon: float,
    radius_km: int = 20
):
    """
    Get hazard reports within a specified radius using PostGIS.
    """

    query = text("""
        SELECT
            id,
            hazard_type,
            severity,
            ST_X(location::geometry) AS lon,
            ST_Y(location::geometry) AS lat
        FROM reports
        WHERE
            location IS NOT NULL
            AND ST_DWithin(
                location::geography,
                ST_SetSRID(
                    ST_MakePoint(:lon, :lat),
                    4326
                )::geography,
                :radius_meters
            )
    """)

    result = db.execute(
        query,
        {
            "lat": lat,
            "lon": lon,
            "radius_meters": radius_km * 1000
        }
    ).fetchall()

    return result


# =========================
# AFFECTED USERS
# =========================

def get_affected_users(
    db: Session,
    hazard_lat: float,
    hazard_lon: float,
    radius_km: int = 20
):
    """
    Get users affected by a hazard.
    """

    users = get_users_in_radius(
        db=db,
        lat=hazard_lat,
        lon=hazard_lon,
        radius_km=radius_km
    )

    return [
        {
            "id": u[0],
            "name": u[1],
            "lat": u[3],
            "lon": u[2]
        }
        for u in users
    ]


# =========================
# CHECK USER IN GEOFENCE
# =========================

def is_user_in_geofence(
    db: Session,
    user_lat: float,
    user_lon: float,
    hazard_lat: float,
    hazard_lon: float,
    radius_km: int = 20
):
    """
    Check whether a user location is inside
    the specified geofence using PostGIS.
    """

    query = text("""
        SELECT ST_DWithin(
            ST_SetSRID(
                ST_MakePoint(:user_lon, :user_lat),
                4326
            )::geography,

            ST_SetSRID(
                ST_MakePoint(:hazard_lon, :hazard_lat),
                4326
            )::geography,

            :radius_meters
        ) AS in_geofence
    """)

    result = db.execute(
        query,
        {
            "user_lat": user_lat,
            "user_lon": user_lon,
            "hazard_lat": hazard_lat,
            "hazard_lon": hazard_lon,
            "radius_meters": radius_km * 1000
        }
    ).scalar()

    return result