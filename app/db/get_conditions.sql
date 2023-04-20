-- :name get_conditions :many
SELECT C.*
FROM aw_vehicle_restriction R
	LEFT JOIN aw_vehicle_restriction_condition C USING (restriction_id)
WHERE R.restriction_id = :restriction_id
