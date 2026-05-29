-- 学院表
CREATE TABLE house(
    house_id INT AUTO_INCREMENT PRIMARY KEY,
    house_name VARCHAR(50) NOT NULL UNIQUE,
    founder VARCHAR(50) NOT NULL,
    total_points INT DEFAULT 0 COMMENT '学院总分，由触发器自动维护'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 初始化学院数据
INSERT INTO house(house_name,founder,total_points) VALUES
('Gryffindor','Godric Gryffindor',0),
('Slytherin','Salazar Slytherin',0),
('Ravenclaw','Rowena Ravenclaw',0),
('Hufflepuff','Helga Hufflepuff',0);

-- 用户表（学生+教授）
CREATE TABLE sys_user(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL COMMENT '建议后端用MD5或bcrypt加密',
    role TINYINT NOT NULL COMMENT '0:学生,1:教授',
    house_id INT COMMENT '外键：所属学院，教授可为空',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_house FOREIGN KEY(house_id) REFERENCES house(house_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 分数记录表
CREATE TABLE point_log(
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL COMMENT '外键：被加扣分的学生',
    professor_id INT NOT NULL COMMENT '外键：操作评分的教授',
    score_change INT NOT NULL COMMENT '分数变动，正数为加分，负数为扣分',
    reason VARCHAR(255) NOT NULL COMMENT '加扣分事由',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_student FOREIGN KEY(student_id) REFERENCES sys_user(user_id),
    CONSTRAINT fk_log_professor FOREIGN KEY(professor_id) REFERENCES sys_user(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 触发器：加分扣分后自动更新学院总分
DELIMITER //
CREATE TRIGGER trg_after_point_insert
AFTER INSERT ON point_log
FOR EACH ROW
BEGIN
    DECLARE target_house_id INT;
    SELECT house_id INTO target_house_id FROM sys_user WHERE user_id = NEW.student_id;
    
    IF target_house_id IS NOT NULL THEN
        UPDATE house 
        SET total_points = total_points + NEW.score_change 
        WHERE house_id = target_house_id;
    END IF;
END //
DELIMITER ;



-- 1. 课程表
CREATE TABLE course (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(100) NOT NULL,        -- 如：魔药学、变形术、黑魔法防御术
    professor_id INT,                          -- 授课教授
    credits INT DEFAULT 2,                     -- 学分
    description TEXT,
    FOREIGN KEY (professor_id) REFERENCES sys_user(user_id)
);

-- 2. 课程安排表
CREATE TABLE course_schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL,
    weekday TINYINT,                          -- 1-7 (周一到周日)
    start_time TIME,                          -- 如：09:00
    end_time TIME,                            -- 如：10:30
    classroom VARCHAR(50),                    -- 如：地下教室、天文塔
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

-- 3. 选课表（多对多关系）
CREATE TABLE course_enrollment (
    enrollment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enroll_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1,                 -- 1=在读, 2=已完成, 3=已退课
    final_score DECIMAL(5,2),                 -- 最终成绩
    FOREIGN KEY (student_id) REFERENCES sys_user(user_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    UNIQUE KEY (student_id, course_id)
);

-- 4. 课堂表现记录表（与积分关联）
CREATE TABLE class_performance (
    performance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    professor_id INT NOT NULL,
    performance_type TINYINT,                 -- 1=回答问题, 2=课堂作业, 3=小组合作
    score INT,                                -- 课堂得分
    point_log_id INT,                         -- 关联到积分记录
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES sys_user(user_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (professor_id) REFERENCES sys_user(user_id),
    FOREIGN KEY (point_log_id) REFERENCES point_log(log_id)
);

