SET TIME ZONE 'UTC';
CREATE USER smart_miner WITH ENCRYPTED PASSWORD 'smartminerpa$$w0rd1368';
CREATE DATABASE smart_miner;
CREATE DATABASE smart_miner_simulation_data;
CREATE DATABASE smart_miner_orders_data;
CREATE DATABASE simulation_smart_miner_orders_data;
/* CREATE TABLE a_simulation(order_id character(200) NOT NULL, moment timestamptz NOT NULL, power_limit DOUBLE PRECISION DEFAULT 0.0, price DOUBLE PRECISION DEFAULT 0.0, CONSTRAINT order_status UNIQUE(order_id, moment)); */
GRANT ALL PRIVILEGES ON DATABASE smart_miner TO smart_miner;
GRANT ALL PRIVILEGES ON DATABASE smart_miner_simulation_data TO smart_miner;
GRANT ALL PRIVILEGES ON DATABASE smart_miner_orders_data TO smart_miner;
GRANT ALL PRIVILEGES ON DATABASE simulation_smart_miner_orders_data TO smart_miner;
\c smart_miner
CREATE TABLE pools (id SERIAL PRIMARY KEY, name character(40) NOT NULL UNIQUE);
INSERT INTO pools (name) VALUES ('slushpool');
CREATE TABLE slushpool (moment timestamptz PRIMARY KEY, hash_rate DOUBLE PRECISION NOT NULL, scoring_hash_rate DOUBLE PRECISION NOT NULL, active_users INT NOT NULL, active_workers INT NOT NULL);
CREATE TABLE network_data (moment timestamptz PRIMARY KEY, network_hash DOUBLE PRECISION NOT NULL, difficulty DOUBLE PRECISION NOT NULL);
CREATE TABLE blocks (id INTEGER PRIMARY KEY, moment timestamptz NOT NULL, pool_id INTEGER NOT NULL, CONSTRAINT fk_pool_id FOREIGN KEY(pool_id) REFERENCES pools(id));
CREATE INDEX blocks_range_query_index on blocks (pool_id, moment, moment desc);
CREATE TABLE key_values (owner character(100), key character(500), value TEXT, CONSTRAINT owner_key_unique UNIQUE(owner, key));
\c smart_miner_simulation_data
CREATE TABLE key_values (owner character(100), key character(500), value TEXT, CONSTRAINT owner_key_unique UNIQUE(owner, key));
\c smart_miner_orders_data
/* TODO add maybe constant for pool_id */
CREATE TYPE nicehash_order_market AS ENUM ('EU','USA','EU_N','USA_E');
CREATE TYPE nicehash_order_algorithm AS ENUM ('SHA250');
CREATE TYPE nicehash_order_type AS ENUM ('standard', 'fixed');
CREATE TABLE IF NOT EXISTS orders (
creation_timestamp timestamptz NOT NULL,
order_id character(200) PRIMARY KEY NOT NULL,
price DOUBLE PRECISION NOT NULL,
speed_limit DOUBLE PRECISION NOT NULL,
amount DOUBLE PRECISION NOT NULL,
market nicehash_order_market NOT NULL,
order_type nicehash_order_type NOT NULL,
algorithm nicehash_order_algorithm NOT NULL,
pool_id character(100) NOT NULL, exist BIT NOT NULL);
CREATE TABLE IF NOT EXISTS stats_order (update_timestamp timestamptz NOT NULL, order_id character(200) NOT NULL, is_order_alive BIT NOT NULL,
accepted_speed DOUBLE PRECISION, rejected_speed_share_above_target DOUBLE PRECISION, rejected_speed_stale_shares DOUBLE PRECISION,
rejected_speed_duplicate_shares DOUBLE PRECISION, rejected_speed_invalid_ntime DOUBLE PRECISION, rejected_speed_other_reason DOUBLE PRECISION,
rejected_speed_unknown_worker DOUBLE PRECISION, rejected_speed_response_timeout DOUBLE PRECISION, speed_limit DOUBLE PRECISION NOT NULL,
rewarded_speed DOUBLE PRECISION NOT NULL, paying_speed DOUBLE PRECISION NOT NULL, rejected_speed DOUBLE PRECISION NOT NULL,
paid_amount DOUBLE PRECISION NOT NULL, price DOUBLE PRECISION NOT NULL, full_details_json_serialized TEXT full_details_json_serialized TEXT);
CREATE TABLE IF NOT EXISTS key_values (owner character(100), key character(500), value TEXT, CONSTRAINT owner_key_unique UNIQUE(owner, key));