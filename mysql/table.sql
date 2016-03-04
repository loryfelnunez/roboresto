create table if not exists restaurant(camis varchar(50), dba varchar(255), cuisine varchar(255), building varchar(25), street varchar(50), boro varchar(50), zip varchar(10), phone varchar(20), primary key (camis));
create table if not exists inspection(camis varchar(50), type varchar(255), inspection_date datetime, score int, action varchar(255), grade varchar(10), grade_date datetime, violation_code varchar(10));
create table if not exists violation(violation_code varchar(10), description varchar(255), critical_flag varchar(10), primary key (violation_code));
