use school;
select * from course;

-- 데이터 생성 
insert into department values(1, '수학');
insert into department values(2, '국문학');
insert into department values(3, '정보통신학');
insert into department values(4, '모바일공학');

insert into student values(1, '가길동', 177, 1);
insert into student values(2, '나길동', 178, 1);
insert into student values(3, '다길동', 179, 1);
insert into student values(4, '라길동', 180, 2);
insert into student values(5, '마길동', 170, 2);
insert into student values(6, '바길동', 172, 3);
insert into student values(7, '사길동', 166, 4);
insert into student values(8, '아길동', 192, 4);

insert into professor values(1, '가교수', 1);
insert into professor values(2, '나교수', 2);
insert into professor values(3, '다교수', 3);
insert into professor values(4, '빌게이츠', 4);
insert into professor values(5, '스티브잡스', 3);

insert into course values(1, '교양영어', 1, '2016/9/2', '2016/11/30');
insert into course values(2, '데이터베이스 입문', 3, '2016/8/20', '2016/10/30');
insert into course values(3, '회로이론', 2, '2016/10/20', '2016/12/30');
insert into course values(4, '공업수학', 4, '2016/11/2', '2017/1/28');
insert into course values(5, '객체지향프로그래밍', 3, '2016/11/1', '2017/1/30');

insert into student_course values(1,1);
insert into student_course values(2,1);
insert into student_course values(3,2);
insert into student_course values(4,3);
insert into student_course values(5,4);
insert into student_course values(6,5);
insert into student_course values(7,5);

-- 문제 1
select s.student_id, s.student_name, s.height, d.department_id, d.department_name 
from student s join department d
on s.department_id = d.department_id;

-- 문제 2
select professor_id from professor where professor_name = '가교수';

-- 문제 3
select department_name, count(professor_id)
from professor
group by department_name;

select d.department_name, count(p.professor_id)
from department d join professor p
on d.department_id = p.department_id
group by department_name;

-- 문제 4
select s.student_id, s.student_name, s.height, d.department_id, d.department_name
from student s join department d
on s.department_id = d.department_id
where student_name = '바길동';

-- 문제 5
select p.professor_id, p.professor_name, d.department_id, d.department_name
from professor p join department d
on p.department_id = d.department_id
where department_name = '정보통신학';

-- 문제 6
select s.student_name, d.department_name
from student s join department d
on s.department_id = d.department_id
where s.student_name like '%아%'; # 문자열은 =가 아니라 like를 써야 함

-- 문제 7
select count(student_id)
from student
where height between 180 and 190; # , 안됨 between A and B임

-- 문제 8
select d.department_name, max(s.height), avg(s.height)
from department d join student s
on d.department_id = s.department_id
group by department_name;

-- 문제 9
select s1.student_name
from student s1 join student s2
on s1.department_id = s2.department_id
where s1.student_name = '다길동';

-- 문제 10
select s.student_name, c.course_name
from student s 
	join student_course sc
	on s.student_id = sc.student_id
	join course c
    on c.course_id = sc.course_id
where c.start_date >= '2016-11-01' and c.start_date <= '2016-12-01';

--  문제 11
select s.student_name
from student s 
	join student_course sc
	on s.student_id = sc.student_id
	join course c
    on sc.course_id = c.course_id
where course_name = '데이터베이스 입문';

-- 문제 12
select count(student_id)
from student s 
	join professor p
	on s.department_id = p.department_id
	join course c
    on p.professor_id = c.professor_id
where professor_name = '빌게이츠';

-- end