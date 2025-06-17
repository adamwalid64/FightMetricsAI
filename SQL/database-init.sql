CREATE DATABASE IF NOT EXISTS ufc_data;
USE ufc_data;


CREATE TABLE ufc_fighters (
    id INT AUTO_INCREMENT NOT NULL,
    name VARCHAR(30),
    nickname VARCHAR(30),
    dob VARCHAR(30),
    age INT NOT NULL,
    height VARCHAR(30),
    weight INT,
    reach DECIMAL(5,2),
    stance VARCHAR(30),
    winstreak INT NOT NULL,
    wins INT NOT NULL,
    losses INT NOT NULL,
    draws INT NOT NULL,
    belt BOOLEAN NOT NULL,
    SLpM DECIMAL(5,2) NOT NULL,
    Str_Acc INT NOT NULL,
    SApM DECIMAL(5,2) NOT NULL,
    Str_Def INT NOT NULL,
    TD_Avg DECIMAL(5,2) NOT NULL,
    TD_Acc INT NOT NULL,
    TD_Def INT NOT NULL,
    Sub_Avg DECIMAL(5,2) NOT NULL,
    PRIMARY KEY (id)
);

SELECT * FROM your_table_name
LIMIT 2000;

SELECT user FROM mysql.user;
