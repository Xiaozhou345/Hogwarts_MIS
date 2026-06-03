-- ============================================
-- 霍格沃茨 MIS - 数据库索引优化脚本
-- 阶段四：系统优化（组员3 余雨航）
-- 创建时间: 2026-06-01
-- 用法: mysql -u root -p < sql/db_indexes.sql
-- 注意: 如索引已存在会报错，忽略即可（不影响数据）
-- ============================================

-- 1. sys_user 表索引
CREATE INDEX idx_user_role ON sys_user(role);
CREATE INDEX idx_user_house ON sys_user(house_id);

-- 2. point_log 表索引
CREATE INDEX idx_point_student ON point_log(student_id);
CREATE INDEX idx_point_professor ON point_log(professor_id);
CREATE INDEX idx_point_time ON point_log(create_time);

-- 3. course 表索引
CREATE INDEX idx_course_professor ON course(professor_id);

-- 4. course_enrollment 表索引
CREATE INDEX idx_enrollment_student ON course_enrollment(student_id);
CREATE INDEX idx_enrollment_course ON course_enrollment(course_id);
CREATE INDEX idx_enrollment_status ON course_enrollment(status);
CREATE INDEX idx_enrollment_student_status ON course_enrollment(student_id, status);

-- 5. course_schedule 表索引
CREATE INDEX idx_schedule_course ON course_schedule(course_id);
CREATE INDEX idx_schedule_weekday ON course_schedule(weekday);

-- 6. class_performance 表索引
CREATE INDEX idx_performance_student ON class_performance(student_id);
CREATE INDEX idx_performance_course ON class_performance(course_id);
CREATE INDEX idx_performance_professor ON class_performance(professor_id);
CREATE INDEX idx_performance_time ON class_performance(create_time);

-- ============================================
-- 验证索引创建结果（逐表查看）
-- ============================================
-- SHOW INDEX FROM sys_user;
-- SHOW INDEX FROM point_log;
-- SHOW INDEX FROM course;
-- SHOW INDEX FROM course_enrollment;
-- SHOW INDEX FROM course_schedule;
-- SHOW INDEX FROM class_performance;
