from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from ..db.database import SessionLocal
from ..models.schemas import RecyclingCenter, WasteCategory
from typing import List, Optional

router = APIRouter()

@router.get("/centers", response_model=List[RecyclingCenter])
async def get_centers():
    with SessionLocal() as db:
        query = text("""
SELECT 
    rc.center_id,
    rc.name,
    rc.description,
    rc.address,
    rc.city,
    rc.state,
    rc.country,
    rc.postal_code,
    rc.latitude,
    rc.longitude,
    rc.phone,
    rc.email,
    rc.website,
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(
                'day', oh.day,
                'opening_time', oh.opening_time,
                'closing_time', oh.closing_time
            )
        ) FILTER (WHERE oh.day IS NOT NULL),
        '[]'::json
    ) as operating_hours,
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(
                'category_id', wc.category_id,
                'name', wc.name,
                'description', wc.description,
                'process', wc.process,
                'tips', wc.tips,
                'icon', wc.icon
            )
        ) FILTER (WHERE wc.category_id IS NOT NULL),
        '[]'::json
    ) as waste_categories
FROM recycling_centers rc
LEFT JOIN operating_hours oh ON rc.center_id = oh.center_id
LEFT JOIN center_waste_categories cwc ON rc.center_id = cwc.center_id
LEFT JOIN waste_categories wc ON cwc.category_id = wc.category_id
GROUP BY rc.center_id;
        """)

        result = db.execute(query)
        centers = result.fetchall()

        # Convert row proxy to dict and handle JSON fields
        return [
            {
                "center_id": row.center_id,
                "name": row.name,
                "description": row.description,
                "address": row.address,
                "city": row.city,
                "state": row.state,
                "country": row.country,
                "postal_code": row.postal_code,
                "latitude": float(row.latitude) if row.latitude else None,
                "longitude": float(row.longitude) if row.longitude else None,
                "phone": row.phone,
                "email": row.email,
                "website": row.website,
                "operating_hours": row.operating_hours if row.operating_hours != '[null]' else [],
                "waste_categories": row.waste_categories if row.waste_categories != '[null]' else []
            }
            for row in centers
        ]


@router.get("/centers/nearby")
async def get_nearby_centers(latitude: float, longitude: float, radius: float = 10.0):
    with SessionLocal() as db:
        query = text("""
            WITH nearby_centers AS (
                SELECT 
                    center_id,
                    name,
                    description,
                    address,
                    city,
                    state,
                    country,
                    postal_code,
                    latitude,
                    longitude,
                    phone,
                    email,
                    website,
                    (6371 * acos(cos(radians(:lat)) * 
                     cos(radians(latitude)) * 
                     cos(radians(longitude) - radians(:lon)) + 
                     sin(radians(:lat)) * 
                     sin(radians(latitude)))) AS distance
                FROM recycling_centers
                WHERE (6371 * acos(cos(radians(:lat)) * 
                       cos(radians(latitude)) * 
                       cos(radians(longitude) - radians(:lon)) + 
                       sin(radians(:lat)) * 
                       sin(radians(latitude)))) < :radius
            )
            SELECT 
                nc.*,
                COALESCE(
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'day', oh.day,
                            'opening_time', oh.opening_time,
                            'closing_time', oh.closing_time
                        )
                    ) FILTER (WHERE oh.day IS NOT NULL),
                    '[]'::json
                ) as operating_hours,
                COALESCE(
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'category_id', wc.category_id,
                            'name', wc.name,
                            'description', wc.description,
                            'process', wc.process,
                            'tips', wc.tips
                        )
                    ) FILTER (WHERE wc.category_id IS NOT NULL),
                    '[]'::json
                ) as waste_categories
            FROM nearby_centers nc
            LEFT JOIN operating_hours oh ON nc.center_id = oh.center_id
            LEFT JOIN center_waste_categories cwc ON nc.center_id = cwc.center_id
            LEFT JOIN waste_categories wc ON cwc.category_id = wc.category_id
            GROUP BY 
                nc.center_id,
                nc.name,
                nc.description,
                nc.address,
                nc.city,
                nc.state,
                nc.country,
                nc.postal_code,
                nc.latitude,
                nc.longitude,
                nc.phone,
                nc.email,
                nc.website,
                nc.distance
            ORDER BY nc.distance
        """)

        result = db.execute(query, {
            "lat": latitude,
            "lon": longitude,
            "radius": radius
        })
        centers = result.fetchall()

        return [
            {
                "center_id": row.center_id,
                "name": row.name,
                "description": row.description,
                "address": row.address,
                "city": row.city,
                "state": row.state,
                "country": row.country,
                "postal_code": row.postal_code,
                "latitude": float(row.latitude) if row.latitude else None,
                "longitude": float(row.longitude) if row.longitude else None,
                "distance": float(row.distance) if row.distance else None,
                "phone": row.phone,
                "email": row.email,
                "website": row.website,
                "operating_hours": row.operating_hours if row.operating_hours != '[null]' else [],
                "waste_categories": row.waste_categories if row.waste_categories != '[null]' else []
            }
            for row in centers
        ]


@router.get("/centers/search")
async def search_centers(
        q: Optional[str] = None,
        city: Optional[str] = None,
        waste_type: Optional[str] = None
):
    with SessionLocal() as db:
        # First get the matching center IDs
        base_query = text("""
            WITH matching_centers AS (
                SELECT DISTINCT rc.center_id
                FROM recycling_centers rc
                LEFT JOIN center_waste_categories cwc ON rc.center_id = cwc.center_id
                LEFT JOIN waste_categories wc ON cwc.category_id = wc.category_id
                WHERE 
                    (:q IS NULL OR 
                        rc.name ILIKE '%' || :q || '%' OR 
                        rc.description ILIKE '%' || :q || '%' OR
                        rc.address ILIKE '%' || :q || '%')
                    AND (:city IS NULL OR rc.city ILIKE '%' || :city || '%')
                    AND (:waste_type IS NULL OR wc.name ILIKE '%' || :waste_type || '%')
            )
            SELECT 
    rc.center_id,
    rc.name,
    rc.description,
    rc.address,
    rc.city,
    rc.state,
    rc.country,
    rc.postal_code,
    rc.latitude,
    rc.longitude,
    rc.phone,
    rc.email,
    rc.website,
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(  -- Cambiado a DISTINCT y jsonb_build_object
                'day', oh.day,
                'opening_time', oh.opening_time,
                'closing_time', oh.closing_time
            )
        ) FILTER (WHERE oh.day IS NOT NULL),
        '[]'::json
    ) as operating_hours,
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(  -- Ya tenías DISTINCT aquí
                'category_id', wc.category_id,
                'name', wc.name,
                'description', wc.description,
                'process', wc.process,
                'tips', wc.tips
                "icon", wc.icon
            )
        ) FILTER (WHERE wc.category_id IS NOT NULL),
        '[]'::json
    ) as waste_categories
FROM recycling_centers rc
LEFT JOIN operating_hours oh ON rc.center_id = oh.center_id
LEFT JOIN center_waste_categories cwc ON rc.center_id = cwc.center_id
LEFT JOIN waste_categories wc ON cwc.category_id = wc.category_id
GROUP BY rc.center_id
        """)

        # Clean up parameters
        params = {
            "q": q.strip() if q else None,
            "city": city.strip() if city else None,
            "waste_type": waste_type.strip() if waste_type else None
        }

        result = db.execute(base_query, params)
        centers = result.fetchall()

        return [
            {
                "center_id": row.center_id,
                "name": row.name,
                "description": row.description,
                "address": row.address,
                "city": row.city,
                "state": row.state,
                "country": row.country,
                "postal_code": row.postal_code,
                "latitude": float(row.latitude) if row.latitude else None,
                "longitude": float(row.longitude) if row.longitude else None,
                "phone": row.phone,
                "email": row.email,
                "website": row.website,
                "operating_hours": row.operating_hours if row.operating_hours != '[null]' else [],
                "waste_categories": row.waste_categories if row.waste_categories != '[null]' else []
            }
            for row in centers
        ]

# Add single center endpoint
@router.get("/centers/{center_id}")
async def get_center(center_id: int):
    with SessionLocal() as db:
        query = text("""
            SELECT 
                rc.center_id,
                rc.name,
                rc.description,
                rc.address,
                rc.city,
                rc.state,
                rc.country,
                rc.postal_code,
                rc.latitude,
                rc.longitude,
                rc.phone,
                rc.email,
                rc.website,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'day', oh.day,
                            'opening_time', oh.opening_time,
                            'closing_time', oh.closing_time
                        )
                    ) FILTER (WHERE oh.day IS NOT NULL),
                    '[]'
                ) as operating_hours,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'category_id', wc.category_id,
                            'name', wc.name,
                            'description', wc.description,
                            'process', wc.process,
                            'tips', wc.tips
                            "icon", wc.icon
                        )
                    ) FILTER (WHERE wc.category_id IS NOT NULL),
                    '[]'
                ) as waste_categories
            FROM recycling_centers rc
            LEFT JOIN operating_hours oh ON rc.center_id = oh.center_id
            LEFT JOIN center_waste_categories cwc ON rc.center_id = cwc.center_id
            LEFT JOIN waste_categories wc ON cwc.category_id = wc.category_id
            WHERE rc.center_id = :center_id
            GROUP BY rc.center_id
        """)

        result = db.execute(query, {"center_id": center_id})
        center = result.fetchone()

        if not center:
            raise HTTPException(status_code=404, detail="Center not found")

        return {
            "center_id": center.center_id,
            "name": center.name,
            "description": center.description,
            "address": center.address,
            "city": center.city,
            "state": center.state,
            "country": center.country,
            "postal_code": center.postal_code,
            "latitude": float(center.latitude) if center.latitude else None,
            "longitude": float(center.longitude) if center.longitude else None,
            "phone": center.phone,
            "email": center.email,
            "website": center.website,
            "operating_hours": center.operating_hours if center.operating_hours != '[null]' else [],
            "waste_categories": center.waste_categories if center.waste_categories != '[null]' else []
        }


@router.get("/waste-categories", response_model=List[dict])
async def get_waste_categories():
    with SessionLocal() as db:
        query = text("""
           SELECT 
               category_id,
               name,
               description,
               status,
               process,
               tips,
               icon,
               created_at,
               updated_at
           FROM waste_categories
           WHERE status = 'active'
           ORDER BY name ASC
       """)

        result = db.execute(query)
        categories = result.fetchall()

        return [
            {
                "category_id": row.category_id,
                "name": row.name,
                "description": row.description,
                "process": row.process,
                "tips": row.tips,
                "icon": row.icon
            }
            for row in categories
        ]