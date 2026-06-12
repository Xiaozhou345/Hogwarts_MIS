-- ============================================
-- 时间转换器功能 - 数据库表结构
-- ============================================

-- 1. 活动表 (activities)
-- 用于存储所有可参加的魔法活动
CREATE TABLE IF NOT EXISTS activity (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    activity_name VARCHAR(100) NOT NULL COMMENT '活动英文名称',
    activity_name_cn VARCHAR(100) NOT NULL COMMENT '活动中文名称',
    weekday TINYINT NOT NULL COMMENT '活动时间：1-7 (周一到周日)',
    start_time TIME NOT NULL COMMENT '开始时间',
    end_time TIME NOT NULL COMMENT '结束时间',
    location VARCHAR(100) COMMENT '活动地点',
    description TEXT COMMENT '活动描述',
    status TINYINT DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_weekday_time (weekday, start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='魔法活动表';

-- 2. 学生活动选课表 (student_activity_enrollment)
-- 记录学生通过时间转换器选择的活动
CREATE TABLE IF NOT EXISTS student_activity_enrollment (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL COMMENT '学生ID',
    activity_id INT NOT NULL COMMENT '活动ID',
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '选择时间',
    status TINYINT DEFAULT 1 COMMENT '状态：1=有效，0=已失效（学院失去第一名）',
    FOREIGN KEY (student_id) REFERENCES sys_user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activity(activity_id) ON DELETE CASCADE,
    UNIQUE KEY uk_student_activity (student_id, activity_id),
    INDEX idx_student_status (student_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生活动选课表';

-- ============================================
-- 初始化活动数据（防止重复插入）
-- ============================================
-- 先清空活动表（如果需要重新初始化）
-- TRUNCATE TABLE activity;

INSERT INTO activity (activity_name, activity_name_cn, weekday, start_time, end_time, location, description, status) VALUES
-- 1. 去海格小屋喝茶
('Tea with Hagrid', '去海格小屋喝茶', 1, '14:00:00', '15:30:00', 'Hagrid\'s Hut', '在海格温馨的小屋里，享受岩皮饼和热茶，听他讲述神奇生物的故事', 1),

-- 2. 去霍格莫德村游玩
('Hogsmeade Village Visit', '去霍格莫德村游玩', 6, '09:00:00', '17:00:00', 'Hogsmeade Village', '探访三把扫帚酒吧、蜂蜜公爵糖果店，体验魔法世界的周末时光', 1),

-- 3. 和打人柳练拳击
('Whomping Willow Training', '和打人柳练拳击', 3, '16:00:00', '17:30:00', 'Whomping Willow Area', '在安全距离内与霍格沃茨最暴躁的树木进行反应训练', 1),

-- 4. 溜进厨房偷家养小精灵的午餐
('Kitchen Raid', '溜进厨房偷家养小精灵的午餐', 2, '12:00:00', '13:00:00', 'Hogwarts Kitchen', '悄悄溜进城堡厨房，品尝家养小精灵准备的美味佳肴（他们其实很欢迎！）', 1),

-- 5. 去双子玩笑店逛逛
('Weasleys\' Wizard Wheezes Visit', '去双子玩笑店逛逛', 5, '15:00:00', '17:00:00', 'Diagon Alley', '参观韦斯莱双胞胎的魔法恶作剧商店，发现最新的整蛊道具', 1),

-- 6. 去禁林收集独角兽的银色血液
('Forbidden Forest Expedition', '去禁林收集独角兽的银色血液', 4, '20:00:00', '22:00:00', 'Forbidden Forest', '在月光下进入禁林，寻找独角兽的踪迹（需要足够的勇气！）', 1),

-- 7. 幻影移形（去和纽特照顾神奇动物）
('Apparition to Newt\'s Sanctuary', '幻影移形（去和纽特照顾神奇动物）', 7, '10:00:00', '16:00:00', 'Newt Scamander\'s Sanctuary', '通过幻影移形前往纽特·斯卡曼德的神奇动物保护区，学习照顾神奇生物', 1);

-- ============================================
-- 创建触发器：当学院失去第一名时，自动删除该学院学生的活动选课
-- ============================================
DELIMITER //

CREATE TRIGGER IF NOT EXISTS trg_after_point_update_check_top_house
AFTER UPDATE ON house
FOR EACH ROW
BEGIN
    DECLARE current_top_house_id INT;
    DECLARE old_top_house_id INT;

    -- 获取当前积分最高的学院ID
    SELECT house_id INTO current_top_house_id
    FROM house
    ORDER BY total_points DESC
    LIMIT 1;

    -- 如果被更新的学院不是当前第一名，则将该学院学生的活动选课状态设为0
    IF OLD.house_id != current_top_house_id AND OLD.total_points >= NEW.total_points THEN
        UPDATE student_activity_enrollment sae
        JOIN sys_user u ON sae.student_id = u.user_id
        SET sae.status = 0
        WHERE u.house_id = OLD.house_id AND sae.status = 1;
    END IF;
END //

DELIMITER ;
