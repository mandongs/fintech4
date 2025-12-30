-- 데이터베이스 만들기
CREATE DATABASE NAVER_DB;
SHOW DATABASES;

-- 데이터베이스 불러오기
USE NAVER_DB;

-- 테이블 만들기
CREATE TABLE if not exists MEMBER 
(MEM_ID CHAR(8) NOT NULL,
MEM_NAME VARCHAR(10) NOT NULL,
MEM_NUMBER TINYINT NOT NULL,
ADDR CHAR(2) NOT NULL,
PHONE1 CHAR(3) NULL,
PHONE2 CHAR(8) NULL,
HEIGHT TINYINT NULL,
DEBUT_DATE DATE NULL);

SELECT * FROM MEMBER;

-- 테이블 속성 수정하기
ALTER TABLE MEMBER MODIFY MEM_ID CHAR(8) NOT NULL PRIMARY KEY;
DESC MEMBER;

-- 테이블 생성하기
CREATE TABLE BUY
(NUM INT NOT NULL PRIMARY KEY,
MEM_ID CHAR(8) NOT NULL,
PROD_NAME CHAR(6) NOT NULL,
GROUP_NAME CHAR(4) NULL,
PRICE INT NOT NULL,
AMOUNT SMALLINT NOT NULL);
DESC BUY;

-- 테이블 수정하기
ALTER TABLE BUY MODIFY NUM INT NOT NULL AUTO_INCREMENT;

-- 테이블 데이터 입력
INSERT INTO BUY(`NUM`,`MEM_ID`,`PROD_NAME`,`GROUP_NAME`,`PRICE`,`AMOUNT`)
VALUES ('1', 'BLK', '지갑', '', '30', '2'),
('2', 'BLK', '맥북프로', '디지털', '1000', '1'),
('3', 'APN', '아이폰', '디지털', '200', '1'),
('4', 'MMU', '아이폰', '디지털', '200', '5'),
('5', 'BLK', '청바지', '패션', '50', '3'),
('6', 'MMU', '에어팟', '디지털', '80', '10'),
('7', 'FRL', '혼공SQL', '서적', '15', '5'),
('8', 'APN', '혼공SQL', '서적', '15', '2'),
('9', 'APN', '청바지', '패션', '50', '1'),
('10', 'MMU', '지갑', '', '30', '1'),
('11', 'APN', '혼공SQL', '서적', '15', '1'),
('12', 'MMU', '지갑', '', '30', '4');

ALTER TABLE member
MODIFY height TINYINT UNSIGNED;

insert into MEMBER(`MEM_ID`,`MEM_NAME`,`MEM_NUMBER`,`ADDR`,`PHONE1`,`PHONE2`,`HEIGHT`,`DEBUT_DATE`)
values ("TWC", "트와이스", 9, "서울", "02", "11111111", '167', "2015-10-19"),
("BLK", "블랙핑크", 4, "경남", "055", "22222222", '163', "2016-08-08"),
("WMN", "여자친구", 6, "경기", "031", "33333333", '166', "2015-01-15"),
("OMY", "오마이걸", 7, "서울", NULL, NULL, '160', "2015-04-21"),
("GRL", "소녀시대", 7, "서울", "02", "44444444", '168', "2007-08-02"),
("ITZ", "잇지", 5, "경남", NULL, NULL, '167', "2019-02-12"),
("RED", "레드벨벳", 4, "경북", "054", "55555555", '161', "2014-08-01"),
('APN', '에이핑크', 6, '경기', '031', '77777777', '164', '2011-02-10'),
('SPC', '우주소녀', 13, '서울', '02', '88888888', '162', '2016-02-25'),
('MMU', '마마무', 4, '전남', '061', '99999999', '165', '2014-06-19');

SELECT * FROM BUY;