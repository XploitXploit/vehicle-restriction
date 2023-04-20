-- endpoint rodizio geozone (zone_id, lat, lon):
SELECT COUNT(*) > 0 true_false
FROM aw_zone Z
WHERE ST_CONTAINS(
        Z.zone_polygon,
        POINT(:lat, :lon)
    )   AND Z.zone_id = :zone_id