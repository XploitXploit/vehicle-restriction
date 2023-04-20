-- :name get_active_restrictions :many
SELECT R.*
FROM aw_vehicle_restriction R
WHERE R.is_active IS TRUE
	AND :query_time BETWEEN R.start_time AND R.end_time
;
