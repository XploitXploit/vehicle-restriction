SELECT vehicle_id, polygon_id
FROM aw_vehicle V, aw_vehicle_restriction_polygon P
WHERE V.vehicle_id IN :vehicle_list
    AND P.polygon_id IN :polygon_list -- care with sqlalchemy param insertion (there is a list expanding flag)
    AND ST_CONTAINS(P.polygon_geom, POINT(V.latitude, V.longitude))
;