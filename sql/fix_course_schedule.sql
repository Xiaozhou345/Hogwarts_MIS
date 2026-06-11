-- 修复课程安排
-- 将周二和周四的安排从魔药学改为黑魔法防御术

-- 1. 查看当前情况
SELECT '当前情况：' as info;
SELECT 
    cs.schedule_id,
    c.course_name,
    CASE cs.weekday 
        WHEN 1 THEN '周一' 
        WHEN 2 THEN '周二' 
        WHEN 3 THEN '周三' 
        WHEN 4 THEN '周四' 
        WHEN 5 THEN '周五' 
        WHEN 6 THEN '周六' 
        WHEN 7 THEN '周日' 
    END as weekday_name,
    cs.start_time,
    cs.classroom
FROM course_schedule cs
JOIN course c ON cs.course_id = c.course_id
ORDER BY cs.weekday, cs.start_time;

-- 2. 修复：将周二15:00和周四10:00的安排改为黑魔法防御术（课程ID=4）
UPDATE course_schedule 
SET course_id = 4 
WHERE schedule_id IN (8, 7);

-- 3. 查看修复后的情况
SELECT '修复后情况：' as info;
SELECT 
    cs.schedule_id,
    c.course_name,
    CASE cs.weekday 
        WHEN 1 THEN '周一' 
        WHEN 2 THEN '周二' 
        WHEN 3 THEN '周三' 
        WHEN 4 THEN '周四' 
        WHEN 5 THEN '周五' 
        WHEN 6 THEN '周六' 
        WHEN 7 THEN '周日' 
    END as weekday_name,
    cs.start_time,
    cs.classroom
FROM course_schedule cs
JOIN course c ON cs.course_id = c.course_id
ORDER BY cs.weekday, cs.start_time;