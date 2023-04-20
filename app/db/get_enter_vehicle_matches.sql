-- :name get_enter_vehicle_matches :many
SELECT
	V.vehicle_id,
	V.vehicle_current_status,
	R.restriction_id,
	C.veh_rest_condition_id,
	C.interval_definition,
	A.veh_rest_action_id,
	A.restriction_status_name,
	A.notification_id
FROM aw_vehicle_restriction R
	LEFT JOIN aw_vehicle_restriction_condition C USING (restriction_id)
	LEFT JOIN aw_vehicle_restriction_polygon P USING (polygon_id)
	LEFT JOIN aw_vehicle_restriction_action A 
		ON A.restriction_id = R.restriction_id AND A.is_on_enter = 1
	LEFT JOIN aw_vehicle V 
		ON V.vehicle_current_status = A.pre_restriction_status_name
			AND V.patent LIKE CONCAT('%', C.plate_pattern)
			AND COALESCE(V.current_zone, -1) = COALESCE(C.zone_id, V.current_zone, -1)
			AND ST_CONTAINS(
				P.polygon_geom, 
				POINT(V.latitude, V.longitude)
			)
WHERE R.is_active IS TRUE
	AND :query_time BETWEEN R.start_time AND R.end_time
	AND V.vehicle_id IS NOT NULL
;
