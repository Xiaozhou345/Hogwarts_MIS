-- ============================================
-- 时间转换器功能 - 数据库表结构（修改版）
-- 活动时间由学生自主安排，不再固定
-- ============================================

-- 1. 活动表 (activities)
-- 活动类型表，不包含固定时间，只包含活动信息
CREATE TABLE IF NOT EXISTS activity (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    activity_name VARCHAR(100) NOT NULL COMMENT '活动英文名称',
    activity_name_cn VARCHAR(100) NOT NULL COMMENT '活动中文名称',
    location VARCHAR(100) COMMENT '活动地点（可选）',
    description TEXT COMMENT '活动描述',
    suggested_duration INT COMMENT '建议时长（分钟），如60表示建议1小时',
    status TINYINT DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='魔法活动类型表';

-- 2. 学生活动选课表 (student_activity_enrollment)
-- 记录学生通过时间转换器选择的活动，包含学生实际安排的时间
CREATE TABLE IF NOT EXISTS student_activity_enrollment (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL COMMENT '学生ID',
    activity_id INT NOT NULL COMMENT '活动ID',
    weekday TINYINT NOT NULL COMMENT '学生安排的星期：1-7 (周一到周日)',
    start_time TIME NOT NULL COMMENT '学生安排的开始时间',
    end_time TIME NOT NULL COMMENT '学生安排的结束时间',
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '选择时间',
    status TINYINT DEFAULT 1 COMMENT '状态：1=有效，0=已失效（学院失去第一名）',
    FOREIGN KEY (student_id) REFERENCES sys_user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activity(activity_id) ON DELETE CASCADE,
    UNIQUE KEY uk_student_time (student_id, weekday, start_time, end_time),
    INDEX idx_student_status (student_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生活动选课表（含实际安排时间）';

-- ============================================
-- 初始化活动数据（7个活动类型）
-- ============================================
INSERT INTO activity (activity_name, activity_name_cn, location, description, suggested_duration, status) VALUES
-- 1. 去海格小屋喝茶
('Tea with Hagrid', '去海格小屋喝茶', 'Hagrid\'s Hut', '在海格温馨的小屋里，享受岩皮饼和热茶，听他讲述神奇生物的故事', 90, 1),

-- 2. 去霍格莫德村游玩
('Hogsmeade Village Visit', '去霍格莫德村游玩', 'Hogsmeade Village', '探访三把扫帚酒吧、蜂蜜公爵糖果店，体验魔法世界的周末时光', 120, 1),

-- 3. 和打人柳练拳击
('Whomping Willow Training', '和打人柳练拳击', 'Whomping Willow Area', '在安全距离内与霍格沃茨最暴躁的树木进行反应训练', 60, 1),

-- 4. 溜进厨房偷家养小精灵的午餐
('Kitchen Raid', '溜进厨房偷家养小精灵的午餐', 'Hogwarts Kitchen', '悄悄溜进城堡厨房，品尝家养小精灵准备的美味佳肴（他们其实很欢迎！）', 60, 1),

-- 5. 去双子玩笑店逛逛
('Weasleys\' Wizard Wheezes Visit', '去双子玩笑店逛逛', 'Diagon Alley', '参观韦斯莱双胞胎的魔法恶作剧商店，发现最新的整蛊道具', 90, 1),

-- 6. 去禁林收集独角兽的银色血液
('Forbidden Forest Expedition', '去禁林收集独角兽的银色血液', 'Forbidden Forest', '在月光下进入禁林，寻找独角兽的踪迹（需要足够的勇气！）', 120, 1),

-- 7. 幻影移形（去和纽特照顾神奇动物）
('Apparition to Newt\'s Sanctuary', '幻影移形（去和纽特照顾神奇动物）', 'Newt Scamander\'s Sanctuary', '通过幻影移形前往纽特·斯卡曼德的神奇动物保护区，学习照顾神奇生物', 180, 1);

-- ============================================
-- 创建触发器：当学院积分变化时，删除所有非第一名学院学生的活动选课
-- ============================================
DELIMITER //

DROP TRIGGER IF EXISTS trg_after_point_update_check_top_house//

CREATE TRIGGER trg_after_point_update_check_top_house
AFTER UPDATE ON house
FOR EACH ROW
BEGIN
    DECLARE current_top_house_id INT;

    -- 获取当前积分最高的学院ID
    SELECT house_id INTO current_top_house_id
    FROM house
    ORDER BY total_points DESC
    LIMIT 1;

    -- 删除所有非第一名学院学生的活动选课记录
    -- 逻辑：只保留第一名学院的活动，其他学院的活动全部删除
    -- 修改原因：
    -- 1. 使用DELETE而不是UPDATE status=0，避免唯一键冲突
    -- 2. 删除所有非第一名学院的活动，而不是只删除被更新学院的活动
    DELETE sae FROM student_activity_enrollment sae
    JOIN sys_user u ON sae.student_id = u.user_id
    WHERE u.house_id != current_top_house_id AND sae.status = 1;
END//

DELIMITER ;