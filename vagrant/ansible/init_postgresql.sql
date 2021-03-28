SET TIME ZONE 'UTC';
CREATE USER smart_miner WITH ENCRYPTED PASSWORD 'smartminerpa$$w0rd1368';
CREATE DATABASE smart_miner;
CREATE DATABASE smart_miner_simulation_data;
/* CREATE TABLE a_simulation(order_id character(200) NOT NULL, moment timestamptz NOT NULL, power_limit DOUBLE PRECISION DEFAULT 0.0, price DOUBLE PRECISION DEFAULT 0.0, CONSTRAINT order_status UNIQUE(order_id, moment)); */
GRANT ALL PRIVILEGES ON DATABASE smart_miner TO smart_miner;
GRANT ALL PRIVILEGES ON DATABASE smart_miner_simulation_data TO smart_miner;
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
