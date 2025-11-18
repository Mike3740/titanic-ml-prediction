Create database if not exists titanic_ml;
use titanic_ml;
drop table if exists train_raw;
create table train_raw (
PassengerId INT,
Survived TINYINT,
Pclass      TINYINT,
  Name        VARCHAR(255),
  Sex         VARCHAR(10),
  Age         VARCHAR(20), 
  SibSp       VARCHAR(20),
  Parch       VARCHAR(20),
  Ticket      VARCHAR(50),
  Fare        VARCHAR(50),
  Cabin       VARCHAR(50),
  Embarked    VARCHAR(5)
);
DROP TABLE IF EXISTS test_raw;
CREATE TABLE test_raw (
  PassengerId INT,
  Pclass      TINYINT,
  Name        VARCHAR(255),
  Sex         VARCHAR(10),
  Age         VARCHAR(20),
  SibSp       VARCHAR(20),
  Parch       VARCHAR(20),
  Ticket      VARCHAR(50),
  Fare        VARCHAR(50),
  Cabin       VARCHAR(50),
  Embarked    VARCHAR(5)
);
UPDATE train_raw
SET Age  = NULLIF(TRIM(Age),  ''),
    Fare = NULLIF(TRIM(Fare), ''),
    SibSp= NULLIF(TRIM(SibSp),''),
    Parch= NULLIF(TRIM(Parch),'');
ALTER TABLE train_raw
  MODIFY PassengerId INT NOT NULL,
  MODIFY Survived    TINYINT,
  MODIFY Pclass      TINYINT,
  MODIFY Age         DECIMAL(5,2) NULL,
  MODIFY SibSp       INT NULL,
  MODIFY Parch       INT NULL,
  MODIFY Fare        DECIMAL(10,4) NULL;
ALTER TABLE train_raw
  ADD PRIMARY KEY (PassengerId);

UPDATE test_raw
SET Age  = NULLIF(TRIM(Age),  ''),
    Fare = NULLIF(TRIM(Fare), ''),
    SibSp= NULLIF(TRIM(SibSp),''),
    Parch= NULLIF(TRIM(Parch),'');
ALTER TABLE test_raw
  MODIFY PassengerId INT NOT NULL,
  MODIFY Pclass      TINYINT,
  MODIFY Age         DECIMAL(5,2) NULL,
  MODIFY SibSp       INT NULL,
  MODIFY Parch       INT NULL,
  MODIFY Fare        DECIMAL(10,4) NULL;
ALTER TABLE test_raw
  ADD PRIMARY KEY (PassengerId);
  SELECT 'train_raw' AS t, COUNT(*) AS n FROM train_raw
UNION ALL
SELECT 'test_raw' , COUNT(*)       FROM test_raw;

