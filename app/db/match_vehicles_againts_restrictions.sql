-- :name match_vehicles_against_restrictions :many
SELECT 
	V.vehicle_id,
	V.vehicle_current_status,
	R.restriction_id,
	C.veh_rest_condition_id,
	C.interval_definition,
	ST_CONTAINS(P.polygon_geom, POINT(V.latitude, V.longitude)) polygon_match
FROM aw_vehicle_restriction R
	LEFT JOIN aw_vehicle_restriction_condition C USING (restriction_id)
	LEFT JOIN aw_vehicle_restriction_polygon P USING (polygon_id)
	LEFT JOIN aw_vehicle V 
		ON V.vehicle_current_status IN (
				'ACTIVE',
				'ON_GOING', 
				'BOOKED', 
				'DEACTIVE', 
				'DISABLED_BY_ZONE', 
				'DISABLED_BY_RODIZIO'
			) 
			AND V.patent LIKE CONCAT('%', C.plate_pattern)
			AND COALESCE(V.current_zone, -1) = COALESCE(C.zone_id, V.current_zone, -1)

WHERE R.is_active IS TRUE
	AND :query_time BETWEEN R.start_time AND R.end_time
	AND V.vehicle_id IS NOT NULL
	AND (
		:match_polygon IS FALSE
		OR ST_CONTAINS(
			P.polygon_geom, 
			POINT(V.latitude, V.longitude)
		)
	)
;
