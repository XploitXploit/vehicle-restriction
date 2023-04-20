CREATE DATABASE test;
CREATE DATABASE test_log;

CREATE TABLE test.aw_vehicle_restriction (
	restriction_id INT AUTO_INCREMENT,
	restriction_name VARCHAR(100) NOT NULL,
	is_active BOOL NOT NULL DEFAULT TRUE,
	creation_date TIMESTAMP
		NOT NULL DEFAULT CURRENT_TIMESTAMP,
	last_modified_date TIMESTAMP
		NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

	start_time TIMESTAMP -- the restriction should be valid between start-end
		NOT NULL DEFAULT '2010-01-01 00:00:00',
	end_time TIMESTAMP
		NOT NULL DEFAULT '2030-01-01 00:00:00',
	PRIMARY KEY (restriction_id)
);

CREATE TABLE test.aw_vehicle_restriction_condition (
	veh_rest_condition_id INT AUTO_INCREMENT,
	restriction_id INT NOT NULL,
	zone_id INT, -- if the vehicle is parked in that zone. null means that that condition will not check
	polygon_id INT,  -- vehicle in that geozone
	interval_definition VARCHAR(200) NOT NULL, -- for example: 'L9:00-3h'.
	plate_pattern VARCHAR(50) NOT NULL, -- a pattern match.
	PRIMARY KEY(veh_rest_condition_id),
	FOREIGN KEY (restriction_id)
		REFERENCES aw_vehicle_restriction (restriction_id)
);

-- this is VERY preliminary and subject to change
/* CARE: what happens if an action is repeated for a restriction? a query would return
 * more than one row for a vehicle that matches. 
 */
CREATE TABLE test.aw_vehicle_restriction_action (
	veh_rest_action_id INT AUTO_INCREMENT,
	restriction_id INT,
	is_on_enter BOOL NOT NULL DEFAULT TRUE,
	pre_restriction_status_name VARCHAR(45) NULL, -- vehicle status to do something
	restriction_status_name VARCHAR(45) NULL, -- new status
	notification_id INT NULL, -- some notification reference
	PRIMARY KEY(veh_rest_action_id),
	FOREIGN KEY (restriction_id) REFERENCES aw_vehicle_restriction (restriction_id)
);

CREATE TABLE test.aw_vehicle_restriction_polygon (
	polygon_id INT AUTO_INCREMENT,
	creation_date TIMESTAMP
		NOT NULL DEFAULT CURRENT_TIMESTAMP, -- only for book-keeping
	polygon_name VARCHAR(100),
	polygon_geom GEOMETRY NOT NULL,
	PRIMARY KEY (polygon_id)
);

CREATE TABLE test_log.aw_vehicle_restriction_log (
	id INT AUTO_INCREMENT,
	log_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	restriction_id INT NOT NULL,
	veh_rest_action_id INT,
	polygon_id INT,
	vehicle_id INT,
	PRIMARY KEY (id)
);

-- pending: create log tables for: restriction, condition, action, polygon
-- so that 'on change' the old values should be stored.
