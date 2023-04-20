-- :name get_enter_status_actions :many
SELECT A.veh_rest_action_id,
	A.restriction_id,
	A.pre_restriction_status_name,
	A.restriction_status_name
FROM aw_vehicle_restriction_action A
WHERE A.restriction_id IN (:restriction_list)
	AND A.is_on_enter IS TRUE
	AND A.restriction_status_name IS NOT NULL
;
