-- endpoint rodizio geozone (zone_id, vehicle_id):
SELECT COUNT(*) > 0 true_false
FROM aw_zone Z
    LEFT JOIN aw_vehicle V ON V.vehicle_id = :vehicle_id
WHERE ST_CONTAINS(
        Z.zone_polygon,
        POINT(V.latitude, V.longitude)
    )   AND Z.zone_id = :zone_id