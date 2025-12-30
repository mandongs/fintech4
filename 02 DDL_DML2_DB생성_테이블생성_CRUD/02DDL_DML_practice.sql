-- DDL을 이용해서 DB만들고 테이블 만들기/삭제하기
-- Create database/schema 데이터베이스 이름;
create database sampledb2;
create database if not exists sampledb2; #없으면 만들어 if not exists #안전하게 충돌하지 않게

-- 데이터베이스 목록 확인: 만들어져 있는지 확인하는 방법  show databases;
show databases;

-- 데이터베이스 열기/사용 use 데이터베이스명
use sampledb2;

-- 데이터베이스 지우기 drop database 데이터베이스명;
drop database sampledb2;
drop database if exists sampled2;

-- sampledb2 다시 만들기
create database if not exists sampledb2;

-- 테이블 만들기 create table if not exists 테이블명 
-- (컬럼이름1 데이터타입 제약조건(not, null, unique), 
-- 컬럼이름2 데이터타입 제약조건(not, null, unique))

use sampledb2; #항상 use 활성화를 했는지, 어떤 DB를 쓸건지 불러와야 함
-- businesscard 테이블 만들기
create table if not exists businesscard (
	name varchar(255) not null, 
	address varchar(255) not null, 
	telephone varchar(15) null);
    
-- 테이블 목록 조회 show tables;
show tables;

-- 테이블의 속성, 제약조건 보기 desc 테이블명;
desc businesscard;

-- 이미 만들어진 테이블의 속성 변경하기 alter
-- name 컬럼을 not null에서 null로 변경
alter table businesscard modify name varchar(100) null;
desc businesscard; 
-- DDL create(만들기), alter(수정하기), drop(삭제하기)truncate(비우기)

-- 만들어진 테이블에 데이터 입력하기 DML insert, update, delete 
-- 데이터 입력하기 insert info 테이블명(컬럼명2, 컬럼명2) values (자료1, 자료2)
insert into  businesscard (`name`, `address`, `telephone`)  #컬럼명은 `으로 감싸줘야 함
values ('bob','서초동 123', '02-1234-5678'),
('sam','서초동 124', '02-1234-5679'),
('bob2','서초동 125', '02-1234-5680');

-- select로 입력된 자료 조회
select * from businesscard;

-- insert into 시 컬럼명 생략하고 자료만 넣기
-- 반드시 컬럼수와 자료 수가 일치, 컬럼명 순서대로 입력해야 함
desc businesscard;
insert into  businesscard (`name`, `address`, `telephone`) 
values ('bob','서초동 123', '02-1234-5678'),
('sam','서초동 124', '02-1234-5679'),
('bob2','서초동 125', '02-1234-5680');

insert into businesscard (`address`)
values ('서초동 126');
select * from businesscard;

insert into  businesscard (`name`, `telephone`) 
values ('bob', '02-1234-5678');

insert into  businesscard values ('bob3','서초동 127', '02-1234-5681');
insert into  businesscard values ('서초동 128','bob4', '02-1234-5682');

insert into  businesscard values ('서초동 128','bob4', '02-1234-5682');

insert into businesscard (`name`, `address`, `telephone`) 
values ('서초동 129','bob5', '02-1234-5683'); # 컬럼명을 적음으로서 컬럼 순서에 따라 넣어줌 # 컬럼명 없으면 순서 이상하게 됨

-- no 컬럼 추가 int null
alter table businesscard add column no int null;

desc businesscard;
select * from businesscard;


insert into  businesscard values ('bob3','서초동 127','02-1234-5681'); # varchar 문자타입, int 숫자타입alter

insert into businesscard (`name`, `address`, `no`, `telephone`) 
values ('서초동 129','bob5', 8, '02-1234-5683');

select * from businesscard;
desc businesscard;

-- Primary key(고유키) Autoincrement(숫자를 자동 증가) 적용하기
alter table businesscard add column idx int not null auto_increment primary key; # idx 인덱스
desc businesscard;
select * from businesscard;

insert into businesscard (`name`, `address`, `no`, `telephone`) 
values ('서초동 130','bob5', 8, '02-1234-5683');

insert into businesscard (`name`, `address`, `no`, `telephone`) 
values ('서초동 131','bob6', 9, '02-1234-5684');

select * from businesscard;


-- auto_increment가 설정된 컬럼이 있는 경우 반드시 컬럼명을 명시해 주어야 함
insert into businesscard
values ('bob8', '서초동 132', 10, '02-1234-5685');

-- --------------------------------------------------------------------

-- 기존 테이블의 자료를 수정하기 update 
-- update 테이블명 set 컬럼1 = 값1, 컬럼2 = 값2 where 조건; # where 조건을 반드시 주어야 함
select * from businesscard;

update businesscard set name = 'bob4', address = '서초동 128' where idx = 6;
update businesscard set name = 'bob6', address = '서초동 130' where idx = 8;
update businesscard set name = 'bob7', address = '서초동 131' where idx = 9;
update businesscard set name = 'bob8', address = '서초동 132' where idx = 10;
update businesscard set no = 1; 

-- 데이터 삭제하기 delete
delete from businesscard where idx = 4;
delete from businesscard;

-- -------------------------------
-- 트랜젝션: 여러 dml을 한 묶음으로 처리하는 것, 중간에 문제가 생기면 
-- rollback으로 되돌리고 문제가 없으면 commit으로 확정
-- autocommit 확인/전환
select @@autocommit; # 1 = on, 0 = off
set autocomit = 0;
select @@autocommit; # 1 = on, 0 = off
start transaction;   
select * from businesscard;
update businesscard set name = 'sam2', telephone = '02-1111-2222' where idx = 16;
commit; # 저장 
rollback; -- DML 명령에서만 rollback 가능. DDL creat, drop, truncate은 rollback이 안됨

set autocommit = 1;
select @@autocommit;
