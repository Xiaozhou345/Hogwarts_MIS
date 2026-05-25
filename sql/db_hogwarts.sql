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