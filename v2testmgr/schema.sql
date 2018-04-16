drop table if exists tb_user;
create table tb_user (
    uid integer primary key autoincrement,
    username text not null,
    --暂不考虑安全问题，直接用明文
    password text not null
);

drop table if exists tb_project;
create table tb_project (
    pid integer primary key autoincrement,
    project text not null,
    uid integer not null,
    status text not null default 'Init',
    mode integer not null default 0
);