INSERT INTO awto.aw_vehicle_restriction (
    restriction_id, restriction_name, start_time, end_time
)
VALUES
    (1, 'chilean_zone_restriction', '2022-01-01', '2022-12-01'),
    (2, 'brazil_rodizio', '2022-01-01', '2022-12-01')
;

INSERT INTO awto.aw_vehicle_restriction_polygon (
    polygon_name, polygon_geom
)
SELECT 'some_polygon', ST_GEOMFROMTEXT('POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))')
-- some nonsense polygon as an example
;

INSERT INTO awto.aw_vehicle_restriction_condition (
    restriction_id, zone_id, polygon_id, interval_definition, plate_pattern
)
VALUES
    (1, 1030, NULL, 'LMWJVSD22:00-8h', '%5'),
    (2, NULL, 1,    'L08:00-3h', '%1'), -- supposing sql-esque pattern matching
    (2, NULL, 1,    'L08:00-3h', '%2'),
    (2, NULL, 1,    'M08:00-3h', '%3'),
    (2, NULL, 1,    'M08:00-3h', '%4'),
    (2, NULL, 1,    'W08:00-3h', '%5'),
    (2, NULL, 1,    'W08:00-3h', '%6'),
    (2, NULL, 1,    'J08:00-3h', '%7'),
    (2, NULL, 1,    'J08:00-3h', '%8'),
    (2, NULL, 1,    'V08:00-3h', '%9'),
    (2, NULL, 1,    'V08:00-3h', '%0')
;

INSERT INTO awto.aw_vehicle_restriction_action (
    restriction_id, is_on_enter, pre_restriction_status_name, restriction_status_name, notification_id
)
VALUES 
    (1, TRUE, 'ACTIVE', 'DEACTIVE_BY_TIME', NULL),
    (1, FALSE, 'DEACTIVE_BY_TIME', 'ACTIVE', NULL),
    (2, TRUE, 'ACTIVE', 'DEACTIVE_BY_RODIZIO', NULL),
    (2, FALSE, 'DEACTIVE_BY_RODIZIO', 'ACTIVE', NULL),
    (2, TRUE, 'ON_GOING', NULL, 1) -- should the second value be 'ON_GOING' or NULL?
;
