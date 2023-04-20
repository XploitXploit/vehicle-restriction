# vehicle-restriction-service
- lead: francisco pellerano
- stakeholder: jose daniel lopez

What follows are the notes refined from meetings and development.

See `notes/sql` for structure, data and query examples.

# Things that have to be thought about
1. how to make rodizio exclusions for special holydays?
    - brute approch, no new implementation required: create restrictions with correct start-end times
    - less brute, more complicated possible approach: have a separate table of intervals to apply the logic (either as inclusion or exclusion)
2. how is the book-keeping of past condition data will be kept on modification?
    - database approach, fast but not maintainable: database trigger on modifications
    - delegate to maintainer
3. restriction maintainer: no words about this yet
4. How to handle the actions 'on leaving' condition?
5. how to reference notification specification on action? @matiasvenegas

# General Requirements
1. For vehicles, use the following information to match and take actions at specific times
    - plate
    - current time (the 'at specific times' part)
    - vehicle location
    - zone of parking
    - vehicle status: after a 'restriction match' some vehicle status are matched with an action
        - may be either status change or,
        - user notification

2. Actions to take: should have some sort of conditional.
    - match && active -> make `deactive_by_rodizio` (the status only as example)
    - nomatch && `deactive_by_rodizio` -> make active
    - match && `in_trip` -> notify via `$some_channel`

3. The actions will be executed by another service, the this service only needs to call some endpoint in the correct moment

4. As a starting point: only (polygon, point) match should be delegated to the database to compute

# Gowgo exposed endpoints (WIP: pending specific definition)

1. all relevant vehicles with status
2. changes in vehicle status (with window as parameter) @josedaniel: this is a new one
    - return vehicle and status for every vehicle that has a modified date later than X seconds ago
3. change status of vehicle
4. notify user via 'some notification channel'

# Service queries/interactions to database
1. get restriction information: query the restriction model to get info

2. query for vehicle / geozone matching
    - given (`vehicle_id_list`, `polygon_id_list`) -> (`vehicle_id`, `polygon_id`) set of matches

3. Vehicles have a pre filtering condition for check versus polygon? STATUS

# data maintainers
WIP: not defined

# the restriction conditions
1. parking zone: optional, restriction match when the vehicle is parked in a zone
2. geozone match: optional, restriction match when a vehicle is inside a geozone
3. time interval: restriction match for the moment defined by an interval
4. plate pattern: optional: restriction match when vehicles plate match pattern

Each restriction has many condition rows, those act as logic ORs. The above listed conditions are enacted as logical ANDs when the values are not NULL.

# Endpoints exposed by the new MS
WIP: detail progress and changes @franciscopellerano
1. match interval with timestamp,tz
    - takes: interval definition, match time, timezone
    - returns: boolean, prev and next timestamps then the match changes

2. match plate with patern
    - takes: plate, pattern
    - returns: bool

3. match point with zone
    - takes: polygon, point (should the polygon be passed as value, or as a id reference?)
    - returns: true/false

4. match vehicle with restriction
    - takes: point, plate, timestamp, tz, `interval_def`, `plate_pattern`, polygon
    - returns: boolean, prev/next timestamps for match change

5. return action to take for a vehicle (here i'm hidding the action match, because as it is now is 'trivial')
    - takes: vehicle
    - returns: action to take

# Time interval definition
The specification defines a unambiguous week recurring time period that must respect some specified local timezone.

## Examples:
1. `L09:00-7d`: whole week
2. `LMW09:00-8h`: Mon, Tue, Wed, the office hours
3. `LM07:00-3h,LM17:00-3h`: Mon, Tue, morning and evening

## Loose difinition
(with some very liberal specification similar to regexp)
- structure: `[days: LMWJVSD]HH:MM-[:digit:][time_units: smhd]`
- possible days: `L`, `M`, `W`, `J`, `V`, `S`, `D`
- `HH:MM` is a 24 hour time with minute definition (not required to have a leading zero)
- time units allowed: `s`, `m`, `h`, `d`. meaninig seconds, minutes, hours, days
- the time magnitude: some integer (WIP: are floating point numbers allowed?) @franciscopellerano
- there may be many patterns separated by commas, each separated interval definition is interpreted as above and the list combined via logical union
    """
        format: 'Xhh:mm-Yu' meaning 'start X day at hh:mm for Y units of
        time separated by commas, spaces ignored
        X, days of the week [L,M,W,J,V,S,D], can insert multiple letters to
        expand
        A -> week days, expands to [L, M, W, J, V]
        B -> week ends, expands to [S,D]
        Y -> integer number
        u -> unit [d, h, m] -> day, hour, minute
        examples:
        'L07:00-2h' mondays from 7:00 to 9:00
        'L00:00-7d' whole week
        'B21:00-8h' expands to 'S21:00-8h,D21:00-8h'
        'AB21:00-h10' = 'LMWJVSD21:00-10h'
        """
## Time Zones
    TZ is a enviroment variable in the configuration settings.

# Scheduler definition
WIP: @franciscopellerano
## Queue/Jobs Definition
    - Multiple queues(dependents jobs???)
        - Retriving vehicles from the database
        - Matching vehicles with restrictions
        - Executing actions
    - Jobs:
        - Retriving vehicles from the database, send dependant jobs
            - Matching vehicles with restrictions, send dependant jobs
                - Executing actions

    Scheduler Methods
        -Add Job
            -Add Job to Queue or Scheduler?
        -Remove Job
            -Remove Job from Queue: 
                when you remove a job from a queue, you have to deleted or only deactivate the job?
        -Update Job
            - Find Job: 
                when you want to update a job, you have to find it first, then you update it.
        -Consume/Execute Job:
            -This part is unclear, but it seems to be the execution of the job, 
                but when you add it to the queue, it is executed.

##  Redis Approach
    - Redis  worker consuption logic is to consume when the worker is idle for the queue,
        can't create a easy logic for jobs consumption
    - Create one job to deal with data gathering, verifing vehicles in restriction and change vehicle status, or divide in 
        3 jobs with respective queues.

## mack proposal
This is not deeply thought out, use the ideas with a critical view.
- have a 'general' event queue with the events to be executed in the present/future
    - question: what should the queue data be?
    - mock with local queue
    - redis or something
    - gowgo prod has pub/sub service

- have a `add_to_queue` method that allows to schedule into the future (remove/update also)
    - mock up as a cron adding and monitoring tasks
- have a `consume_queue` method set that in the future will execute
    - mock as print con console
    
## Scheduler
We are using redis+fastapi to verify if the vehicles are in a restriction. This happen every 70 seconds, 
this is because gowgo check for the vehicle in a 1 min window. This scheduler triggers a verification function
that check for date interval, plate pattern and if the position(lat/long) is in a polygon. If the vehicle checks
this conditions and given the status of the vehicle, we send a notification to the user or we deactivate the car.

# Proyect Arquitecture
We are using docker and docker-compose for orchestration. 
    -docker-compose build: rebuilds the needed images.
    -docket-compose up: start the aplication

## Gowgo exposed endpoint notes
From meeting from @matiasvenegas

1. `GET getVehicles`: todos los vehiculos con su estado y posicion
- `vehicle_id`
- `lat`
- `lon`
- `vehicle_current_status` (pendiente @matiasvenegas)

2. `GET getTrips`: Recibir todos los trips que están en marcha y reservados (auto caché con spring)
- `trip_id`
- `trip_status`
- `booking_date`
- `start_date`
- `end_date`
- `vehicle`
- `vehicle_id`
- `patent`
- `user`
- `user_id`
- `full_name`
- `email`
- Validations: none

3. `POST editVehicle`: Para poder cambiar la imagen del vehiculo, y cambiar estado
Care that this endpoint is not structured.
- `vehicle_ids: {1,2,4}`
- `params: {“img”, “vehicle_status”}`
- `values: {“wwwww….”, “ACTIVE” }`

4.  Validations:
- vehicle ids exist
- params exist

5. `sendUserMessage`:
A row in `aw_notification_template` must exist.
- `user_id`
- `template_name`
- `params: {“USER_NAME”: “hola”, …}` <- template parameters
    - have a `add_to_queue` method that allows to schedule into the future (remove/update also)
    - mock up as a cron adding and monitoring tasks
    - have a `consume_queue` method set that in the future will execute
    - mock as print con console

# Notes on logic and border conditions
```text
TODO: @fpellerano handle and delete, or format :)
on enter:

restriction
	condition (fk)
		polygon (fk)
	action (fk & on_enter)

	vehicle (plate_pattern, action_status_match, zone, polygon)

where active_restriction & restriction_on_time & vehicle_not_null

for (restriction, interval_definition, vehicle, action)
	check time match and take action 

on exit:

restriction
	condition (fk)
		polygon (fk)
	action (fk & on_exit)

	vehicle (plate_pattern, action_status_match, zone, polygon)

where vehicle_not_null (note that there is not enforcement over restriction status/time)

for (restriction, vehicle, action, [interval_definition set])
	if interval definition set has no matches, then take action
-------------------------------------------

1. what happens when a pooling cycle has many actions for the same vehicle?
	- different actions
		- same restriction -> data integrity problem. TODO: how to enforce from database?
		- different restriction -> maybe a priority? 'defined behavior' must be guaranteed
	- same action repeated
		- same restriction -> care to do not apply action more than one time ('limit 1' / 'distinct')
		- different restriction -> degenerate case fo the diff action, diff restr. (same behavior)
```
