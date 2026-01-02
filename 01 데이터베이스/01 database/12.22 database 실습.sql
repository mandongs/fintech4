-- 데이터베이스 목록 조회 
show databases;

-- 데이터베이스 열기 / excel 파일 더블 클릭하기
use sakila;

-- 테이블 목록 조회 
show tables;

-- 테이블에서 원하는 자료 조회하기 select 컬럼명 (*) from 테이블명;
select * from film;

-- film 테이블에서 title과 release_year 컬럼만 보고 싶을 때
select title, release_year from film;

-- 컬럼 별명, 별칭 주기 (as)
select title as 영화제목, rental_rate 대여요금 from film;

-- 특정 조건을 만족하는 행만 출력하기 (where절)
-- select 컬럼명 from 테이블명 where 조건
-- 문자 조건 where 컬럼명 = "조건"
-- rating이 PG인 행만 조회하고 싶을 때
select * from film where rating = "PG";

-- 숫자 조건 where 컬럼명 = 숫자, > (초과), < (미만), >= (이상), <= (이하)
-- rental_rate가 3 초과인 행 조회
select * from film where rental_rate > 3;

-- 2가지 이상의 조건을 만족하는 행 조회 and, or
-- and 조건 1과 조건 2를 모두 만족하는 경우
-- or 조건 1 혹은 조건 2 중에서 하나만 충족해도 조회 가능
-- film 테이블에서 rental_rate가 2 이상이고, rating이 PG-13인 행 조회
select * from film where rental_rate >= 2 and rating = "PG-13";

-- film 테이블에서 rating이 "PG" 혹은 "G"인 행 조회
select * from film where rating = "PG" or "G";

-- 부정조건 ~가 아닌 경우 <>, !=
-- film 테이블에서 rating이 "PG"가 아닌 행 조회
select * from film where rating != "PG";
select * from film where rating <> "PG";

-- 컬럼끼리 비교하기 
-- replacement_cost가 rental_rate보다 큰 영화만 보기
select title, rental_rate, replacement_cost 
from film 
where replacement_cost > rental_rate;

-- 사칙연산으로 계산한 결과를 조건에 넣을 수 있음
-- replacement_cose - rental_rate 가 >= 10 행만 조회
select title, rental_rate, replacement_cost
from film
where (replacement_cost - rental_rate) >= 10;

-- 날짜 조건 주기 (날짜도 문자처럼 따옴표로 감싸서 조건 줌)
-- rental_date가 2005-07-01 보다 큰 행만 조회
select * from rental where rental_date >= "2005-07-01";

-- between 시작과 끝 값을 포함하는 범위로 조회할 때 (이상, 이하인 경우만 쓸 수 있음)
-- rental_rate >= 2 and rental_rate <= 4 (2,3,4)
-- rental_rate가 2 이상 4 이하인 데이터 조회
select * from film where rental_rate between 2 and 4;

-- in 여러 값 중에서 하나라도 같으면 포함되는 조건 or를 여러번 쓴 것과 같음
-- rating이 'PG', 'G', "PG-13" 일 경우 조회
-- select * from film where rating = 'PG' or rating = 'G' or rating = 'PG-13';
select * from film where rating in ('PG', 'G', "PG-13");

-- like 문자열에 특정 글자가 포함되어 있는지 확인하는 기능
select * from film;
-- description 컬럼에서 drama가 포함된 행 조회
-- select * from film where description = "drama"; (where에서 =은 같은 값만 나오게 함)
-- like "%단어%" (단어가 들어가 있는 것 모두), like "%단어" (단어로 끝나는 모든 것), like "단어%"(단어로 시작하는 모든 것)
select * from film where description like "%drama%";
select * from film where description like "A Epic%";
select * from film where description like "%India";

-- null 조회, 값이 없는 경우 찾기 is null(o), where original_language_id = null (x)
select * from film where original_language_id is null;

-- null이 아닌 것만 조회 is not null
select * from film where original_language_id is not null;

-- 순서 정렬하기 order by, 제한된 숫자 행만 보기 limit
-- 정렬 order by asc(오름차순), order by desc(내림차순)
-- rental_rate 컬럼을 기준으로 내림차순 정렬
select * from film order by rental_rate desc;

-- 두개 이상의 기준으로 정렬하고 싶을 때
-- rating을 기준으로 오름차순 정렬 한 것을 rental_rate 기준으로 내림차순 해서 보기
select * from film order by rating asc, rental_rate desc;

-- 전체 데이터에서 임의의 10행을 추출할 때 rand(), limit 10
-- film 테이블에서 10개의 데이터를 무작위로 추출
select * from film order by rand() limit 10;

-- film 데이터를 3개만 출력 limit 3
select * from film limit 3;

-- 중복 값을 한 번만 출력하는 기능 distinct
select distinct rating from film;

-- 집게함수: 여러 값을 계산해서 하나로 만드는 거 (개수, 평균, 최대, 최소)
-- count 개수
-- sum 합게
-- avg 평균
-- max 최대
-- min 최소
-- 영화 개수 구하기 count
select count(*) as 영화수 from film;

-- rental_rate의 평균, 최고, 최소 요금 계산하기
select 
avg(rental_rate) as 평균요금,
max(rental_rate) as 최고요금,
min(rental_rate) as 최저요금
from film; 

select * from paymeny;
-- payment 테이블의 amount 총합
select sum(amount) 총결제금액 from payment;
-- as 생략해도 됨

-- group by, having
-- group by는 같은 값끼리 묶는 기능, 같은 종류끼리 묶어서 통계를 보고 싶을 때
-- 영화 등급이 같은 영화의 수를 세고 싶을 때
select rating, count(*) as 영화수 from film group by rating;
-- select *, count(*) as 영화수 from film group by rating; 오류

-- having: group by를 한 결과에서 원하는 조건을 줄 때 (where과 다름)
-- group by 에 조건을 주고 싶을 떄 where은 오류가 남. having을 써야함
-- select rating, count(*) as 영화수 from film group by rating where count(*) >= 200; (x)
select rating, count(*) as 영화수 from film group by rating having count(*) >= 200;

-- join: 서로 다른 테이블을 하나의 결과처럼 연결하는 방법. 공통된 컬럼을 기준으로 연결
-- 공통된 컬럼은 보통 primary key, foreign key으로 연결되어 있음
-- inner(합치는 테이블 양쪽에 모두 있는 데이트만 합침)
-- left(합치는 테이블 중 왼쪽 테이블 기준으로 왼쪽에 있는 것만 오른쪽에서 가져옴)
-- right(합치는 테이블 중 오른쪽 테이블을 기준으로 오른쪽에 있는 것만 왼쪽에서 가져옴)

select * from customer;
select * from rental;

-- customer 테이블과 rental 테이블을 합쳐서 이름, 성, 대여일 조회
select c.first_name, c.last_name, r.rental_date # c와 r을(약자) 정확히 명시해줘야 오류가 안 남
from customer c # customer를 c로 부르겠다는 의미
inner join rental r
on c.customer_id = r.customer_id; 

select c.first_name, c.last_name, r.rental_date # c와 r을(약자) 정확히 명시해줘야 오류가 안 남
from customer c # customer를 c로 부르겠다는 의미
left join rental r
on c.customer_id = r.customer_id; 

select c.first_name, c.last_name, r.rental_date # c와 r을(약자) 정확히 명시해줘야 오류가 안 남
from customer c # customer를 c로 부르겠다는 의미
right join rental r
on c.customer_id = r.customer_id; 

-- 테이블 합치고 조건을 주어 필터링 하기
-- 2005-07-01 보다 최근인 자료만 필터링
select c.first_name, c.last_name, r.rental_date # c와 r을(약자) 정확히 명시해줘야 오류가 안 남
from customer c # customer를 c로 부르겠다는 의미
right join rental r
on c.customer_id = r.customer_id
where r.rental_date >= "2005-07-01";

-- join 후에 고객별 대여 횟수 구하기
select c.customer_id, count(r.rental_id) as 대여횟수
from customer c
left join rental r
on c.customer_id = r.customer_id
group by c.customer_id
having count(r.rental_id) >= 10
order by 대여횟수 desc;

-- 1
select * from actor;
-- 2
select first_name, last_name from actor;
-- 3
select title as 영화제목 from film;
-- 4
select email, first_name, last_name from customer;
-- 5
select * from payment;
-- 6
select * from film where rating = 'PG';
-- 7
select title from film where rental_rate > 3;
-- 8
select title, rental_rate, rating from film where rental_rate >= 2 and rating = 'PG-13';
-- 9
select title, rating from film where rating = 'PG' or rating = 'G';
# or, and은 rating = 이 동일하게 들어가야 계산이 됨
-- 10
select title, rental_rate from film where rental_rate between 2 and 4;
# between 숫자, 숫자 (x) between 숫자 and 숫자 (o)
-- 11
select title, rating from film where rating in ('PG', 'G', 'PG-13');
# in 'PG', 'G', 'PG-13'(x) in ('PG', 'G', 'PG-13') (o)
# in은 연산자여서 in()임 항상
-- 12 
select * from customer where email is null;
-- 13
Select title from film where title like '%LOVE%';
-- 14
select title from film where title like 'A%';
-- 15
select title from film where title like '%MAN';
-- 16
select * from customer where last_name like '% %';
# 공백 포함 like '% %'
-- 17
select * from actor where first_name like '%JO%';
-- 18
select * from film order by rental_rate desc;
# 금액이 높은 순서 = 내림차순 desc, 금액이 낮은 순서 = 오름차순 asc
# order by는 where이랑 같이 오지 않음
-- 19
select * from film order by rating asc, rental_rate desc;
-- 20
select title from film order by rental_rate desc limit 5;
-- 21
select * from actor limit 10;
-- 22
select * from customer order by first_name asc limit 20;
-- 23
select * from film order by rating asc limit 3;
-- 24
select distinct rating from film;
# Select distinct ㅇㅇ 중복 없이 조회
-- 25 
select count(*) as 영화수 from film;
-- 26
select avg(rental_rate) as 평균요금 from film;
-- 27
select max(rental_rate) as 최고요금 from film;
-- 28
select min(rental_rate) as 최저요금 from film;
-- 29
select sum(amount) as 총금액 from payment;
-- 30
select avg(amount) as 평균결제금액 from payment;
-- 31
-- select count(*) from film group by rating; (x)
select rating, count(*) as 영화수 from film group by rating;
# group by ㅇㅇ에 적은 것은 select 뒤에도 적어야 함
-- 32
select rating, avg(rental_rate) as 평균대여요금 from film group by rating;
-- 33
select rating from film group by rating having count(title) >= 200;
select rating, count(*) as 영화수 from film group by rating having count(*) >= 200;
-- 34
select staff_id, sum(amount) as 총금액 from payment group by staff_id;
-- 35
select staff_id, sum(amount) as 총결제금액 from payment group by staff_id having amount >= 5000;
select staff_id, sum(amount) as 총결제금액 from payment group by staff_id having sum(amount) >= 5000;
-- 36
select customer_id, count(*) as 결제횟수 from payment group by customer_id;
-- 37
select customer_id, count(*) as 결제횟수 from payment group by customer_id having count(*) >= 30;
-- 38
select customer_id, sum(amount) as 총결제금액 from payment group by customer_id;
-- 39
select c.last_name, c.first_name, r.rental_date 
from customer c inner join rental r
on c.customer_id = r.customer_id;
# 어렵다
-- 40
select c.customer_id, count(r.rental_id) as 대여횟수
from customer c left join rental r # 손님 명단 + 대여 기록장 붙임
on c.customer_id = r.customer_id # 같은 손님끼리만 연결
group by c.customer_id; # 손님 변호별로 묶음
-- 41
select c.customer_id, count(r.rental_id) as 대여횟수
from customer c left join rental r
on c.customer_id = r.customer_id
group by c.customer_id
having 대여횟수 >= 20;
-- 43
select c.customer_id, sum(a.amount) as 총결제금액
from customer c join payment a
on c.customer_id = a.customer_id
group by c.customer_id
having sum(a.amount) >= 100;
-- 44
select c.customer_id, sum(p.amount) as 총결제금액
from customer c join payment p
on c.customer_id = p.customer_id
group by c.customer_id
order by 총결제금액 desc
limit 5;
-- 45
select c.customer_id, r.rental_id
from customer c left join rental r
on c.customer_id = r.customer_id;
-- 46
select c.customer_id 
from customer c left join rental r
on c.customer_id = r.customer_id
where r.rental_id is null;
-- 47
select *
from payment
where amount < 1 or amount is null;
-- 48 
SELECT c.customer_id,
       COUNT(r.rental_id) AS 대여횟수,
       SUM(p.amount) AS 총결제금액
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY c.customer_id;
-- 49
SELECT c.customer_id,
       COUNT(r.rental_id) AS 대여횟수,
       SUM(p.amount) AS 총결제금액
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
group by c.customer_id
having 대여횟수 >= 10 and 총결제금액 >= 50;
-- 50
select c.customer_id, count(r.rental_id) as 대여횟수, sum(p.amount) as 총결제금액
from customer c left join rental r
on c.customer_id = r.customer_id
left join payment p on r.rental_id = p.rental_id
group by c.customer_id
order by 대여횟수 desc, 총결제금액 desc
limit 10;