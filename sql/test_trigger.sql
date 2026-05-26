SELECT '========================================' AS '';
SELECT '触发器验证测试开始' AS '';
SELECT '========================================' AS '';

-- 1. 查看触发器是否存在
SELECT '>>> 步骤1: 检查触发器 trg_after_point_insert 是否存在' AS '';
SHOW TRIGGERS LIKE 'point_log';

-- 2. 记录加分前各学院总分
SELECT '>>> 步骤2: 加分前学院总分' AS '';
SELECT house_id, house_name, total_points FROM house ORDER BY house_id;

-- 3. 保存格兰芬多加分前总分
SET @before_points = (SELECT total_points FROM house WHERE house_id = 1);
SELECT CONCAT('格兰芬多加分前总分: ', @before_points) AS '';

-- 4. 确保有测试数据（如果没有就创建）
SELECT '>>> 步骤3: 确保测试学生和教授存在' AS '';

INSERT IGNORE INTO sys_user (username, password_hash, role, house_id)
VALUES ('trigger_test_student', 'test_sha256_hash', 0, 1);

INSERT IGNORE INTO sys_user (username, password_hash, role, house_id)
VALUES ('trigger_test_professor', 'test_sha256_hash', 1, NULL);

SET @student_id = (SELECT user_id FROM sys_user WHERE username = 'trigger_test_student');
SET @professor_id = (SELECT user_id FROM sys_user WHERE username = 'trigger_test_professor');

SELECT CONCAT('学生ID: ', @student_id, ', 教授ID: ', @professor_id) AS '';

-- 5. 插入积分记录（这会触发 trg_after_point_insert）
SELECT '>>> 步骤4: 插入积分记录 (+50分)' AS '';
INSERT INTO point_log (student_id, professor_id, score_change, reason)
VALUES (@student_id, @professor_id, 50, 'SQL触发器测试-加分50');

SELECT CONCAT('已插入积分记录, log_id = ', LAST_INSERT_ID()) AS '';

-- 6. 查看刚插入的积分记录
SELECT '>>> 步骤5: 刚插入的积分记录' AS '';
SELECT * FROM point_log ORDER BY log_id DESC LIMIT 1;

-- 7. 记录加分后各学院总分
SELECT '>>> 步骤6: 加分后学院总分' AS '';
SELECT house_id, house_name, total_points FROM house ORDER BY house_id;

-- 8. 比对结果
SET @after_points = (SELECT total_points FROM house WHERE house_id = 1);
SELECT CONCAT('格兰芬多加分后总分: ', @after_points) AS '';
SELECT CONCAT('总分变动: +', @after_points - @before_points) AS '';

-- 9. 判断触发器是否生效
SELECT '>>> 步骤7: 判定结果' AS '';

SELECT CASE
    WHEN @after_points = @before_points + 50
    THEN '【PASS】触发器工作正常！学院总分正确增加了50分'
    ELSE CONCAT('【FAIL】触发器未生效！预期 ', @before_points + 50, '，实际 ', @after_points)
END AS '测试结论';

SELECT '========================================' AS '';
SELECT '触发器验证测试结束' AS '';
SELECT '========================================' AS '';
