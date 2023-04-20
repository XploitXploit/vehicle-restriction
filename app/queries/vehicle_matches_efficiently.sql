/* TODO: conditions over vehicle_restriction (active, relevant, etc...) */
/* this query pushes part of the MS logic to the database, so the data lookup is efficient */
SELECT
    R.restriction_id, C.veh_rest_condition_id, P.polygon_id, V.vehicle_id, /* base information for match tracking */
    C.interval_definition, V.vehicle_current_status, T.trip_id, T.status, T.user_id /* info for MS logic */
FROM aw_vehicle_restriction R
    LEFT JOIN aw_vehicle_restriction_condition C USING (restriction_id)
    LEFT JOIN aw_vehicle_restriction_polygon P USING (polygon_id)
    LEFT JOIN aw_vehicle V
            ON COALESCE(C.zone_id, V.current_zone, -1) = COALESCE(V.current_zone, -1) /* only match if C.zone_id is not null */
                AND (C.plate_pattern IS NULL OR V.patent LIKE C.plate_pattern) /* note, logically: p -> q <-> !p or q */
                AND (P.polygon_id IS NULL OR ST_CONTAINS(P.polygon_geom, POINT(V.latitude, V.longitude))) /* same trick as above, only apply condition if P.polygon_id IS NOT NULL */
                /* AND V.vehicle_current_status IN (...) TODO: only match vehicles in a valid status (no SOLD, LOST, etc...) */
    LEFT JOIN aw_trip T
            ON V.vehicle_id = T.car_id 
                AND V.current_user_id = T.user_id /* this match is not logically necessary, but uses indexes that improve query performance */
                AND T.status IN (1, 2) /* only booked and ongoing trips */
WHERE C.veh_rest_condition_id IS NOT NULL
    AND V.vehicle_id IS NOT NULL
;
