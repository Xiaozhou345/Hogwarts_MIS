SET SQL_SAFE_UPDATES = 0;

DELETE FROM class_performance WHERE 1=1;
DELETE FROM course_enrollment WHERE 1=1;
DELETE FROM point_log WHERE 1=1;
DELETE FROM course_schedule WHERE 1=1;
DELETE FROM course WHERE 1=1;
DELETE FROM sys_user WHERE username LIKE 'demo_%';

SET SQL_SAFE_UPDATES = 1;