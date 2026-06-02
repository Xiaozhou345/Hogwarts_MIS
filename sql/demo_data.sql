-- 霍格沃茨 MIS 演示数据

-- 1. 插入教授（4名）
INSERT INTO sys_user (username, password_hash, role, house_id) VALUES
('demo_prof_snape',    SHA2('123456', 256), 1, NULL),
('demo_prof_mcgonagall', SHA2('123456', 256), 1, NULL),
('demo_prof_flitwick', SHA2('123456', 256), 1, NULL),
('demo_prof_sprout',   SHA2('123456', 256), 1, NULL);


-- 2. 插入学生（每个学院5人，共20人）
-- 格兰芬多 (house_id=1)
INSERT INTO sys_user (username, password_hash, role, house_id) VALUES
('demo_harry',   SHA2('123456', 256), 0, 1),
('demo_hermione',SHA2('123456', 256), 0, 1),
('demo_ron',     SHA2('123456', 256), 0, 1),
('demo_ginny',   SHA2('123456', 256), 0, 1),
('demo_neville', SHA2('123456', 256), 0, 1);
-- 斯莱特林 (house_id=2)
INSERT INTO sys_user (username, password_hash, role, house_id) VALUES
('demo_draco',   SHA2('123456', 256), 0, 2),
('demo_pansy',   SHA2('123456', 256), 0, 2),
('demo_blaise',  SHA2('123456', 256), 0, 2),
('demo_daphne',  SHA2('123456', 256), 0, 2),
('demo_theodore',SHA2('123456', 256), 0, 2);
-- 拉文克劳 (house_id=3)
INSERT INTO sys_user (username, password_hash, role, house_id) VALUES
('demo_luna',    SHA2('123456', 256), 0, 3),
('demo_cho',     SHA2('123456', 256), 0, 3),
('demo_padma',   SHA2('123456', 256), 0, 3),
('demo_anthony', SHA2('123456', 256), 0, 3),
('demo_terry',   SHA2('123456', 256), 0, 3);
-- 赫奇帕奇 (house_id=4)
INSERT INTO sys_user (username, password_hash, role, house_id) VALUES
('demo_cedric',  SHA2('123456', 256), 0, 4),
('demo_hannah',  SHA2('123456', 256), 0, 4),
('demo_ernie',   SHA2('123456', 256), 0, 4),
('demo_justin',  SHA2('123456', 256), 0, 4),
('demo_zacharias', SHA2('123456', 256), 0, 4);


-- 3. 插入课程（8门，每个教授2门）
-- 斯内普教授
INSERT INTO course (course_name, professor_id, credits, description) VALUES
('魔药学', (SELECT user_id FROM sys_user WHERE username='demo_prof_snape'), 3, '学习各种魔药的配制方法'),
('黑魔法防御术', (SELECT user_id FROM sys_user WHERE username='demo_prof_snape'), 3, '对抗黑魔法的防御技巧');
-- 麦格教授
INSERT INTO course (course_name, professor_id, credits, description) VALUES
('变形术', (SELECT user_id FROM sys_user WHERE username='demo_prof_mcgonagall'), 3, '物体变形的基础魔法'),
('阿尼玛格斯', (SELECT user_id FROM sys_user WHERE username='demo_prof_mcgonagall'), 4, '高级变形术，变成动物形态');
-- 弗立维教授
INSERT INTO course (course_name, professor_id, credits, description) VALUES
('魔咒学', (SELECT user_id FROM sys_user WHERE username='demo_prof_flitwick'), 3, '各种实用魔咒，如漂浮咒、开锁咒'),
('决斗俱乐部', (SELECT user_id FROM sys_user WHERE username='demo_prof_flitwick'), 2, '练习决斗技巧与魔法防御');
-- 斯普劳特教授
INSERT INTO course (course_name, professor_id, credits, description) VALUES
('草药学', (SELECT user_id FROM sys_user WHERE username='demo_prof_sprout'), 2, '神奇植物的照料与使用'),
('神奇生物保护', (SELECT user_id FROM sys_user WHERE username='demo_prof_sprout'), 3, '学习保护神奇生物');


-- 4. 插入课程安排（每门课程至少2个时间）
-- 魔药学 (周一 09:00-10:00，周三 14:00-15:00)
INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES
((SELECT course_id FROM course WHERE course_name='魔药学' LIMIT 1), 1, '09:00:00', '10:00:00', '地下教室'),
((SELECT course_id FROM course WHERE course_name='魔药学' LIMIT 1), 3, '14:00:00', '15:00:00', '地下教室');
-- 黑魔法防御术 (周二 09:00-10:00，周四 14:00-15:00)
INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES
((SELECT course_id FROM course WHERE course_name='黑魔法防御术' LIMIT 1), 2, '09:00:00', '10:00:00', '黑魔法防御教室'),
((SELECT course_id FROM course WHERE course_name='黑魔法防御术' LIMIT 1), 4, '14:00:00', '15:00:00', '黑魔法防御教室');
-- 变形术 (周二 14:00-15:00，周四 09:00-10:00)
INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES
((SELECT course_id FROM course WHERE course_name='变形术' LIMIT 1), 2, '14:00:00', '15:00:00', '变形教室'),
((SELECT course_id FROM course WHERE course_name='变形术' LIMIT 1), 4, '09:00:00', '10:00:00', '变形教室');
-- 阿尼玛格斯 (周一 11:00-12:00，周五 14:00-15:00)
INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES
((SELECT course_id FROM course WHERE course_name='阿尼玛格斯' LIMIT 1), 1, '11:00:00', '12:00:00', '高级变形室'),
((SELECT course_id FROM course WHERE course_name='阿尼玛格斯' LIMIT 1), 5, '14:00:00', '15:00:00', '高级变形室');
-- 魔咒学 (周一 15:00-16:00，周三 09:00-10:00)
INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES
((SELECT course_id FROM course WHERE course_name='魔咒学' LIMIT 1), 1, '15:00:00', '16:00:00', '魔咒教室'),
((SELECT course_id FROM course WHERE course_name='魔咒学' LIMIT 1), 3, '09:00:00', '10:00:00', '魔咒教室');
-- 决斗俱乐部 (周一 11:00-12:00，周五 09:00-10:00)
INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES
((SELECT course_id FROM course WHERE course_name='决斗俱乐部' LIMIT 1), 1, '11:00:00', '12:00:00', '决斗台'),
((SELECT course_id FROM course WHERE course_name='决斗俱乐部' LIMIT 1), 5, '09:00:00', '10:30:00', '决斗台');
-- 草药学 (周一 14:00-15:00，周三 11:00-12:00)
INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES
((SELECT course_id FROM course WHERE course_name='草药学' LIMIT 1), 1, '14:00:00', '15:00:00', '温室'),
((SELECT course_id FROM course WHERE course_name='草药学' LIMIT 1), 3, '11:00:00', '12:00:00', '温室');
-- 神奇生物保护 (周二 11:00-12:00，周四 11:00-12:00)
INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES
((SELECT course_id FROM course WHERE course_name='神奇生物保护' LIMIT 1), 2, '11:00:00', '12:00:00', '禁林边缘'),
((SELECT course_id FROM course WHERE course_name='神奇生物保护' LIMIT 1), 4, '11:00:00', '12:00:00', '禁林边缘');


-- 5. 插入选课记录
SET @course_potions     = (SELECT course_id FROM course WHERE course_name='魔药学' LIMIT 1);
SET @course_dada        = (SELECT course_id FROM course WHERE course_name='黑魔法防御术' LIMIT 1);
SET @course_transfig    = (SELECT course_id FROM course WHERE course_name='变形术' LIMIT 1);
SET @course_animagus    = (SELECT course_id FROM course WHERE course_name='阿尼玛格斯' LIMIT 1);
SET @course_charms      = (SELECT course_id FROM course WHERE course_name='魔咒学' LIMIT 1);
SET @course_duel        = (SELECT course_id FROM course WHERE course_name='决斗俱乐部' LIMIT 1);
SET @course_herbology   = (SELECT course_id FROM course WHERE course_name='草药学' LIMIT 1);
SET @course_creatures   = (SELECT course_id FROM course WHERE course_name='神奇生物保护' LIMIT 1);

INSERT IGNORE INTO course_enrollment (student_id, course_id, status) VALUES
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @course_potions, 1),
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @course_dada, 1),
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @course_transfig, 1),
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @course_duel, 1),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @course_potions, 1),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @course_transfig, 1),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @course_charms, 1),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @course_animagus, 1),
((SELECT user_id FROM sys_user WHERE username='demo_ron'), @course_potions, 1),
((SELECT user_id FROM sys_user WHERE username='demo_ron'), @course_dada, 1),
((SELECT user_id FROM sys_user WHERE username='demo_ginny'), @course_dada, 1),
((SELECT user_id FROM sys_user WHERE username='demo_ginny'), @course_duel, 1),
((SELECT user_id FROM sys_user WHERE username='demo_neville'), @course_herbology, 1),
((SELECT user_id FROM sys_user WHERE username='demo_neville'), @course_potions, 1);

INSERT IGNORE INTO course_enrollment (student_id, course_id, status) VALUES
((SELECT user_id FROM sys_user WHERE username='demo_draco'), @course_potions, 1),
((SELECT user_id FROM sys_user WHERE username='demo_draco'), @course_dada, 1),
((SELECT user_id FROM sys_user WHERE username='demo_draco'), @course_creatures, 1),
((SELECT user_id FROM sys_user WHERE username='demo_pansy'), @course_charms, 1),
((SELECT user_id FROM sys_user WHERE username='demo_pansy'), @course_transfig, 1),
((SELECT user_id FROM sys_user WHERE username='demo_blaise'), @course_dada, 1),
((SELECT user_id FROM sys_user WHERE username='demo_blaise'), @course_duel, 1),
((SELECT user_id FROM sys_user WHERE username='demo_daphne'), @course_potions, 1),
((SELECT user_id FROM sys_user WHERE username='demo_theodore'), @course_herbology, 1);

INSERT IGNORE INTO course_enrollment (student_id, course_id, status) VALUES
((SELECT user_id FROM sys_user WHERE username='demo_luna'), @course_charms, 1),
((SELECT user_id FROM sys_user WHERE username='demo_luna'), @course_duel, 1),
((SELECT user_id FROM sys_user WHERE username='demo_luna'), @course_herbology, 1),
((SELECT user_id FROM sys_user WHERE username='demo_cho'), @course_transfig, 1),
((SELECT user_id FROM sys_user WHERE username='demo_cho'), @course_potions, 1),
((SELECT user_id FROM sys_user WHERE username='demo_padma'), @course_charms, 1),
((SELECT user_id FROM sys_user WHERE username='demo_padma'), @course_creatures, 1),
((SELECT user_id FROM sys_user WHERE username='demo_anthony'), @course_dada, 1),
((SELECT user_id FROM sys_user WHERE username='demo_terry'), @course_animagus, 1);

INSERT IGNORE INTO course_enrollment (student_id, course_id, status) VALUES
((SELECT user_id FROM sys_user WHERE username='demo_cedric'), @course_dada, 1),
((SELECT user_id FROM sys_user WHERE username='demo_cedric'), @course_duel, 1),
((SELECT user_id FROM sys_user WHERE username='demo_cedric'), @course_herbology, 1),
((SELECT user_id FROM sys_user WHERE username='demo_hannah'), @course_herbology, 1),
((SELECT user_id FROM sys_user WHERE username='demo_hannah'), @course_potions, 1),
((SELECT user_id FROM sys_user WHERE username='demo_ernie'), @course_transfig, 1),
((SELECT user_id FROM sys_user WHERE username='demo_justin'), @course_charms, 1),
((SELECT user_id FROM sys_user WHERE username='demo_zacharias'), @course_creatures, 1);


-- 6. 插入积分记录
-- 获取教授ID（用于积分记录的 professor_id）
SET @prof_snape    = (SELECT user_id FROM sys_user WHERE username='demo_prof_snape');
SET @prof_mcgonagall = (SELECT user_id FROM sys_user WHERE username='demo_prof_mcgonagall');
SET @prof_flitwick = (SELECT user_id FROM sys_user WHERE username='demo_prof_flitwick');
SET @prof_sprout   = (SELECT user_id FROM sys_user WHERE username='demo_prof_sprout');

INSERT INTO point_log (student_id, professor_id, score_change, reason) VALUES
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @prof_snape, 20, '魔药课成功配置福灵剂'),
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @prof_mcgonagall, -5, '变形术课迟到'),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @prof_flitwick, 30, '魔咒学展示完美漂浮咒'),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @prof_mcgonagall, 10, '变形术作业优秀'),
((SELECT user_id FROM sys_user WHERE username='demo_ron'), @prof_snape, -8, '魔药课坩埚爆炸'),

((SELECT user_id FROM sys_user WHERE username='demo_ginny'), @prof_flitwick, 15, '决斗俱乐部获胜'),
((SELECT user_id FROM sys_user WHERE username='demo_neville'), @prof_sprout, 12, '草药学成功培育曼德拉草'),
((SELECT user_id FROM sys_user WHERE username='demo_draco'), @prof_snape, 15, '魔药课提问回答正确'),
((SELECT user_id FROM sys_user WHERE username='demo_draco'), @prof_snape, -10, '决斗中违规使用恶咒'),
((SELECT user_id FROM sys_user WHERE username='demo_pansy'), @prof_flitwick, 5, '魔咒学作业优秀'),

((SELECT user_id FROM sys_user WHERE username='demo_blaise'), @prof_snape, 8, '黑魔法防御术论文优秀'),
((SELECT user_id FROM sys_user WHERE username='demo_daphne'), @prof_mcgonagall, -3, '变形作业潦草'),
((SELECT user_id FROM sys_user WHERE username='demo_theodore'), @prof_sprout, 7, '神奇生物保护课堂积极'),
((SELECT user_id FROM sys_user WHERE username='demo_luna'), @prof_flitwick, 25, '自创魔咒得到认可'),
((SELECT user_id FROM sys_user WHERE username='demo_luna'), @prof_flitwick, 5, '决斗中运用巧妙战术'),

((SELECT user_id FROM sys_user WHERE username='demo_cho'), @prof_mcgonagall, 12, '变形课堂积极'),
((SELECT user_id FROM sys_user WHERE username='demo_padma'), @prof_sprout, 10, '草药学实践满分'),
((SELECT user_id FROM sys_user WHERE username='demo_anthony'), @prof_snape, 6, '黑魔法防御术实战表现良好'),
((SELECT user_id FROM sys_user WHERE username='demo_terry'), @prof_mcgonagall, 20, '成功完成阿尼玛格斯变形'),
((SELECT user_id FROM sys_user WHERE username='demo_cedric'), @prof_snape, 40, '黑魔法防御术实战演练满分'),

((SELECT user_id FROM sys_user WHERE username='demo_cedric'), @prof_snape, -8, '魔药课未携带魔杖'),
((SELECT user_id FROM sys_user WHERE username='demo_hannah'), @prof_sprout, 18, '草药学课堂表现突出'),
((SELECT user_id FROM sys_user WHERE username='demo_ernie'), @prof_mcgonagall, 8, '变形术小组合作优秀'),
((SELECT user_id FROM sys_user WHERE username='demo_justin'), @prof_flitwick, 12, '魔咒学对抗赛胜利'),
((SELECT user_id FROM sys_user WHERE username='demo_zacharias'), @prof_sprout, 6, '神奇生物保护作业完成'),

((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @prof_snape, 5, '魔药课配料精准'),
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @prof_flitwick, 15, '魔咒考试全班第一'),
((SELECT user_id FROM sys_user WHERE username='demo_draco'), @prof_mcgonagall, -3, '变形作业潦草'),
((SELECT user_id FROM sys_user WHERE username='demo_luna'), @prof_snape, 10, '黑魔法防御论据精彩'),
((SELECT user_id FROM sys_user WHERE username='demo_cedric'), @prof_flitwick, 20, '魔咒对抗赛获胜');


-- 7. 插入课堂表现记录
INSERT INTO class_performance (student_id, course_id, professor_id, performance_type, score, point_log_id) VALUES
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @course_potions, @prof_snape, 1, 20, 
 (SELECT log_id FROM point_log WHERE reason='魔药课成功配置福灵剂' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @course_charms, @prof_flitwick, 1, 30,
 (SELECT log_id FROM point_log WHERE reason='魔咒学展示完美漂浮咒' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @course_transfig, @prof_mcgonagall, 2, 10,
 (SELECT log_id FROM point_log WHERE reason='变形术作业优秀' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_draco'), @course_potions, @prof_snape, 1, 15,
 (SELECT log_id FROM point_log WHERE reason='魔药课提问回答正确' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_luna'), @course_charms, @prof_flitwick, 1, 25,
 (SELECT log_id FROM point_log WHERE reason='自创魔咒得到认可' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_luna'), @course_duel, @prof_flitwick, 3, 5,
 (SELECT log_id FROM point_log WHERE reason='决斗中运用巧妙战术' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_cedric'), @course_dada, @prof_snape, 1, 40,
 (SELECT log_id FROM point_log WHERE reason='黑魔法防御术实战演练满分' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @course_duel, @prof_flitwick, 3, 15,
 (SELECT log_id FROM point_log WHERE reason='魔咒考试全班第一' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @course_animagus, @prof_mcgonagall, 2, 25,
 (SELECT log_id FROM point_log WHERE reason='成功完成阿尼玛格斯变形' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_cedric'), @course_duel, @prof_flitwick, 3, 20,
 (SELECT log_id FROM point_log WHERE reason='魔咒对抗赛获胜' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_hermione'), @course_potions, @prof_snape, 2, 5,
 (SELECT log_id FROM point_log WHERE reason='魔药课配料精准' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_cho'), @course_transfig, @prof_mcgonagall, 1, 12,
 (SELECT log_id FROM point_log WHERE reason='变形课堂积极' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_hannah'), @course_herbology, @prof_sprout, 1, 18,
 (SELECT log_id FROM point_log WHERE reason='草药学课堂表现突出' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_draco'), @course_dada, @prof_snape, 1, 8,
 (SELECT log_id FROM point_log WHERE reason='黑魔法防御术论文优秀' LIMIT 1)),
((SELECT user_id FROM sys_user WHERE username='demo_harry'), @course_potions, @prof_snape, 2, -15,
 (SELECT log_id FROM point_log WHERE reason='魔药课坩埚爆炸' LIMIT 1));


-- 8. 验证统计信息
SELECT '========== 演示数据统计（扩大版） ==========' AS '';
SELECT COUNT(*) AS '教授数量' FROM sys_user WHERE role=1 AND username LIKE 'demo_%';
SELECT COUNT(*) AS '学生数量' FROM sys_user WHERE role=0 AND username LIKE 'demo_%';
SELECT COUNT(*) AS '课程数量' FROM course;
SELECT COUNT(*) AS '课程安排数量' FROM course_schedule;
SELECT COUNT(*) AS '选课记录数' FROM course_enrollment;
SELECT COUNT(*) AS '积分记录数' FROM point_log;
SELECT COUNT(*) AS '课堂表现记录数' FROM class_performance;