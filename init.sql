DROP DATABASE IF EXISTS `test`;

DROP DATABASE IF EXISTS `test_log`;

CREATE DATABASE `test`;

CREATE DATABASE `test_log`;

CREATE TABLE `test`.aw_vehicle_restriction (
    restriction_id INT AUTO_INCREMENT,
    restriction_name VARCHAR(100) NOT NULL,
    is_active BOOL NOT NULL DEFAULT TRUE,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_modified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    start_time TIMESTAMP -- the restriction should be valid between start-end
    NOT NULL DEFAULT '2010-01-01 00:00:00',
    end_time TIMESTAMP NOT NULL DEFAULT '2030-01-01 00:00:00',
    PRIMARY KEY (restriction_id)
);

CREATE TABLE `test`.aw_vehicle_restriction_condition (
    veh_rest_condition_id INT AUTO_INCREMENT,
    restriction_id INT NOT NULL,
    zone_id INT,
    -- if the vehicle is parked in that zone. null means that that condition will not check
    polygon_id INT,
    -- vehicle in that geozone
    interval_definition VARCHAR(200) NOT NULL,
    -- for example: 'L9:00-3h'.
    plate_pattern VARCHAR(50) NOT NULL,
    -- a pattern match.
    PRIMARY KEY(veh_rest_condition_id),
    FOREIGN KEY (restriction_id) REFERENCES aw_vehicle_restriction (restriction_id)
);

-- this is VERY preliminary and subject to change
/* CARE: what happens if an action is repeated for a restriction? a query would return
 * more than one row for a vehicle that matches. 
 */
CREATE TABLE `test`.aw_vehicle_restriction_action (
    veh_rest_action_id INT AUTO_INCREMENT,
    restriction_id INT,
    is_on_enter BOOL NOT NULL DEFAULT TRUE,
    pre_restriction_status_name VARCHAR(45) NULL,
    -- vehicle status to do something
    restriction_status_name VARCHAR(45) NULL,
    -- new status
    notification_id INT NULL,
    notification_time INT NULL,
    -- some notification reference
    PRIMARY KEY(veh_rest_action_id),
    FOREIGN KEY (restriction_id) REFERENCES aw_vehicle_restriction (restriction_id)
);

CREATE TABLE `test`.aw_vehicle_restriction_polygon (
    polygon_id INT AUTO_INCREMENT,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- only for book-keeping
    polygon_name VARCHAR(100),
    polygon_geom GEOMETRY NOT NULL,
    PRIMARY KEY (polygon_id)
);

CREATE TABLE `test_log`.aw_vehicle_restriction_log (
    id INT AUTO_INCREMENT,
    log_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    restriction_id INT NOT NULL,
    veh_rest_action_id INT,
    polygon_id INT,
    vehicle_id INT,
    PRIMARY KEY (id)
);

CREATE TABLE `test`.aw_vehicle (
    vehicle_id int auto_increment primary key,
    vehicle_name varchar(45) null,
    vehicle_number_plate varchar(45) null,
    vehicle_model varchar(45) null,
    vehicle_type varchar(45) null,
    type_of_operation varchar(45) null,
    vehicle_image_url varchar(254) null,
    current_zone varchar(45) null,
    vehicle_price decimal(14, 4) null,
    vehicle_status tinyint(1) null,
    vehicle_current_status varchar(45) null,
    inventory_status tinyint(1) null,
    vehicle_make varchar(50) null,
    box_num varchar(50) null,
    provider_device_id int unsigned null,
    external_device_id varchar(50) null,
    box_model varchar(50) null,
    sim_provider varchar(50) null,
    transmission varchar(50) null,
    combustible varchar(50) null,
    fuel_percent decimal(14, 4) null,
    patent varchar(100) null,
    device_id varchar(100) null,
    external_provider varchar(100) null,
    observation varchar(512) null,
    kilometer double null,
    fleet_vehicle_id int null,
    latitude decimal(18, 9) null,
    longitude decimal(18, 9) null,
    current_user_id int null,
    creation_date timestamp default CURRENT_TIMESTAMP null,
    last_modified_date timestamp default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    vehicle_segment_id int null,
    priority varchar(10) null,
    voltage decimal(14, 4) null,
    cv int null,
    cvl int null,
    ignition_on tinyint(1) null,
    model_year int(4) null,
    num_chasis varchar(50) null,
    purchase_date timestamp null,
    install_date timestamp null,
    device_model varchar(50) null,
    device_version varchar(45) null,
    sim_card bigint(50) null,
    temporal_parking tinyint(1) default 0 null,
    disconnection_device_check tinyint default 1 not null,
    cron_voltage decimal(14, 4) default 0.0000 null,
    last_sync_position timestamp default CURRENT_TIMESTAMP null,
    key_status tinyint null
);

CREATE TABLE test.aw_trip (
    trip_id int auto_increment primary key,
    user_id int null,
    status varchar(45) null,
    car_id int null,
    start_time timestamp null,
    end_time timestamp null,
    usage_time decimal(14, 4) null,
    stand_by_time decimal(14, 4) null,
    distance_travel decimal(14, 4) null,
    waver_stand_by_time decimal(14, 4) null,
    price_id int null,
    extra_start_time int null,
    extra_end_time int null,
    start_zone int null,
    end_zone int null,
    booking_time timestamp null,
    trip_type varchar(100) null,
    parking_slot int null,
    vehicle_kilometer double null,
    member_ship_id int null,
    migrated_trip_id varchar(100) null,
    closed_by int null,
    promo_coupon_id int null,
    process_tag int(1) null,
    smartreport_message text null
);

CREATE TABLE test.aw_user (
    user_id int auto_increment primary key,
    fname varchar(100) not null,
    lname varchar(50) null,
    email_id varchar(100) not null,
    password varchar(254) not null,
    mobile_no varchar(45) null,
    residence varchar(45) null,
    rut_no varchar(45) null,
    facebook_app_id varchar(300) null,
    google_app_id varchar(100) null,
    registration_step varchar(45) null,
    role_id int null,
    awto_credit_id int null,
    creation_date timestamp default CURRENT_TIMESTAMP null,
    last_modified_date timestamp default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    address_id int null,
    user_type varchar(45) not null,
    gender varchar(45) null,
    pin varchar(45) null,
    token_id int null,
    referal_code varchar(45) null,
    rest_token varchar(254) null,
    coupon_refered_code varchar(254) null,
    reference_type varchar(254) null,
    trip_count decimal(14, 4) null,
    trip_total_amount decimal(14, 4) null,
    total_in_use_time decimal(14, 4) null,
    total_in_stand_by_time decimal(14, 4) null,
    total_trip_time decimal(14, 4) null,
    passport_num varchar(20) null,
    client_id varchar(100) null,
    login_detail int null,
    mig_user_first_time_login int null,
    suspendedby int null,
    blockMembership tinyint(1) default 0 null,
    migrated_password varchar(254) null,
    force_verify int(1) default 0 null,
    last_force_verify timestamp null,
    last_force_verify_status int(1) null,
    license_type int default 0 null,
    has_selfie tinyint default 0 null,
    send_payment_method_email tinyint default 0 null,
    transfer_files tinyint default 0 null,
    tos_version varchar(10) default '1.0.0' null,
    id_colppy int null,
    origin_country_id int null,
    reservation_blocking_time timestamp null,
    by_pass_reservation_blocking tinyint(1) default 0 null,
    birthday date null,
    license_expiration date null,
    pending_debt_email_sent_date timestamp null,
    last_update_ref_code_date timestamp null,
    document_type_id int null,
    apple_app_id varchar(100) null,
    permission_role_id int default 1 not null
);

CREATE TABLE `test_log`.aw_vehicle_restriction_on_going_log (
    id INT AUTO_INCREMENT,
    log_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    restriction_id INT NOT NULL,
    veh_rest_action_id INT,
    polygon_id INT,
    vehicle_id INT,
    ongoing_user INT,
    PRIMARY KEY (id)
);

create table test.aw_notification_template (
    id int auto_increment,
    name varchar(100) not null,
    type_id int not null,
    title varchar(100) not null,
    content text null,
    extra_data text null,
    valid tinyint(1) null,
    creation_date timestamp default CURRENT_TIMESTAMP not null,
    PRIMARY KEY (id)
);


create table `test`.aw_vehicle_restriction_blacklist (
    id int auto_increment,
    vehicle_model varchar(15) not null,
    PRIMARY KEY (id)
);