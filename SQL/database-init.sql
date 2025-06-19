CREATE DATABASE IF NOT EXISTS ufc_data;
USE ufc_data;

-- Initialize Starter DB
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

SELECT * FROM ufc_data.ufc_fighters LIMIT 5000;

SELECT user FROM mysql.user;

-- DATA CLEANING

USE ufc_data;

CREATE VIEW clean_ufc_fights AS
SELECT *
FROM ufc_data.ufc_fighters
WHERE 
    age IS NOT NULL
    AND SLpM != 0.00
    AND Str_Acc != 0
    AND SApM != 0.00
    AND Str_Def != 0
    AND TD_Avg != 0.00
    AND TD_Acc != 0
    AND TD_Def != 0
    AND Sub_Avg != 0.00;

