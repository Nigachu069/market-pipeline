create table IF not exists market_data (
    id serial primary key,
    symbol varchar(10) not null,
    open numeric(10, 2),
    high numeric(10, 2),
    low numeric(10, 2),
    close numeric(10, 2),
    volume BIGINT,
    candle_time timestamp not null,
    inserted_time timestamp default now()
);