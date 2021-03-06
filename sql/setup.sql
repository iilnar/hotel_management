DROP DATABASE IF EXISTS hoteldb;
CREATE DATABASE hoteldb;

USE hoteldb;

DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS room;
DROP TABLE IF EXISTS room_category;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS hotel;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS manager;


CREATE TABLE IF NOT EXISTS hotel
(
  id        INT(11) PRIMARY KEY                                        NOT NULL AUTO_INCREMENT,
  name      VARCHAR(80)                                                NOT NULL,
  url       VARCHAR(255),
  longitude DOUBLE                                                     NOT NULL,
  latitude  DOUBLE                                                     NOT NULL,
  address   VARCHAR(100)                                               NOT NULL,
  image_url VARCHAR(255),
  city      VARCHAR(45)                                                NOT NULL,
  stars     TINYINT                                                    NOT NULL,
  rating    FLOAT                                                               DEFAULT 0,
  budget    INT                                                                 DEFAULT 0
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS manager
(
  sid      BIGINT PRIMARY KEY,
  login    VARCHAR(32) NOT NULL,
  password VARCHAR(32) NOT NULL
)
  ENGINE InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS staff
(
  passport    BIGINT PRIMARY KEY   NOT NULL,
  salary      INT                  NOT NULL,
  first_name  VARCHAR(28)          NOT NULL,
  last_name   VARCHAR(28)          NOT NULL,
  position    ENUM
              ('cleaning',
               'manager',
               'concierge',
               'kitchen_staff',
               'administrator')    NOT NULL,
  hid         INT                  NOT NULL,
  FOREIGN KEY (hid) REFERENCES hotel (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS room_category (
  id           INT         NOT NULL AUTO_INCREMENT,
  type         VARCHAR(45) NOT NULL,
  for_disabled TINYINT(1)           DEFAULT '0',
  max          TINYINT(2)  NOT NULL,
  breakfast    TINYINT(1)           DEFAULT '0',
  parking      INT(1)               DEFAULT '0',
  PRIMARY KEY (id)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS feedback
(
  id       INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  hid      INT(11)             NOT NULL,
  feedback VARCHAR(255),
  rating   INT(11)             NOT NULL,
  FOREIGN KEY (hid) REFERENCES hotel (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;


CREATE TABLE IF NOT EXISTS room
(
  id          INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  hid         INT(11)             NOT NULL,
  rcid        INT(11)             NOT NULL,
  price       INT(11)             NOT NULL,
  room_number INT(11)             NOT NULL,
  image_url   VARCHAR(255),
  FOREIGN KEY (hid) REFERENCES hotel (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (rcid) REFERENCES room_category (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  UNIQUE (hid, room_number)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;


CREATE TABLE IF NOT EXISTS users
(
  id         INT(11) PRIMARY KEY NOT NULL,
  first_name VARCHAR(45)         NOT NULL,
  last_name  VARCHAR(255)        NOT NULL
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;


CREATE TABLE IF NOT EXISTS booking
(
  id             INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  rid            INT(11)             NOT NULL,
  uid            INT(11)             NOT NULL,
  check_in       DATE                NOT NULL,
  check_out      DATE                NOT NULL,
  money          INT                 NOT NULL,
  booking_date   DATETIME                     DEFAULT now(),
  status         TINYINT                      DEFAULT '1',
  FOREIGN KEY (rid) REFERENCES room (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (uid) REFERENCES users (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

DELIMITER $$

CREATE TRIGGER date_validation_trigger
BEFORE INSERT ON booking
FOR EACH ROW
  BEGIN
    DECLARE msg VARCHAR(64);
    IF (new.check_in < now())
    THEN
      SET msg = concat('date_validation_trigger: past date: ', cast(new.check_in AS CHAR));
      SIGNAL SQLSTATE '46000'
      SET MESSAGE_TEXT = msg;
    END IF;

END $$

CREATE TRIGGER availability_trigger
BEFORE INSERT ON booking
FOR EACH ROW
  BEGIN
    DECLARE msg VARCHAR(128);
    IF (SELECT count(*)
        FROM booking b
        WHERE new.rid = b.rid AND
              ((b.check_in <= new.check_in AND b.check_out >= new.check_in) OR
               (b.check_in <= new.check_out AND b.check_out >= new.check_out))

              > 0
    )
    THEN
      SET msg = concat('availability_trigger: not available: ', cast(new.check_in AS CHAR), ' - ',
                       cast(new.check_out AS CHAR));
      SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = msg;
    END IF;
  END $$

CREATE TRIGGER budgetIncrease
AFTER INSERT ON booking
FOR EACH ROW
  BEGIN
    UPDATE hotel h
    SET budget = budget + new.money
    WHERE h.id IN (SELECT r.hid
                   FROM room r
                   WHERE r.id = new.rid);
  END $$

CREATE TRIGGER budgetDecrease
AFTER DELETE ON booking
FOR EACH ROW
  BEGIN
    UPDATE hotel h
    SET budget = budget - old.money
    WHERE h.id IN (SELECT r.hid
                   FROM room r
                   WHERE r.id = old.rid);
  END $$


CREATE TRIGGER dateTrigger
BEFORE INSERT ON booking

FOR EACH ROW
  BEGIN
    DECLARE msg VARCHAR(64);
    IF (new.check_out < new.check_in)
    THEN
      SET msg = concat('dateTrigger: invalid date interval: ', cast(new.check_in AS CHAR), ' - ',
                       cast(new.check_out AS CHAR));
      SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = msg;
    END IF;


  END $$

CREATE TRIGGER name_validation_trigger
AFTER INSERT ON users
FOR EACH ROW
  BEGIN
    DECLARE msg VARCHAR(64);
    IF ((SELECT new.first_name REGEXP "^([a-z]|-)+$" = 0) OR (SELECT new.last_name REGEXP "^([a-z]|-)+$" = 0))
    THEN
      SET msg = concat('name_validation_trigger: invalid name: ', cast(new.first_name AS CHAR), ' ',
                       cast(new.last_name AS CHAR));
      SIGNAL SQLSTATE 'ERROR'
      SET MESSAGE_TEXT = msg;
    END IF;
  END $$

DROP TRIGGER IF EXISTS username_validation_trigger;
CREATE TRIGGER username_validation_trigger
AFTER INSERT ON users
FOR EACH ROW
  BEGIN
    DECLARE msg VARCHAR(64);
    IF (SELECT new.first_name REGEXP "^([0-9]|[a-z]|-|_|\\.)+$" = 0)
    THEN
      SET msg = concat('name_validation_trigger: invalid name: ', cast(new.first_name AS CHAR), ' ',
                       cast(new.last_name AS CHAR));
      SIGNAL SQLSTATE 'ERROR'
      SET MESSAGE_TEXT = msg;
    END IF;
  END $$

CREATE TRIGGER adding_manager
AFTER INSERT ON staff
FOR EACH ROW
  BEGIN
    IF (new.position = 'manager' OR new.position = 'administrator')
    THEN
      INSERT INTO manager (sid, login, password) VALUES
        (new.passport, concat(new.position, cast(new.passport AS CHAR)),
         concat(new.position, cast(new.passport AS CHAR)));
    END IF;
  END $$

DELIMITER ;
