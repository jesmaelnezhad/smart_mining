SET TIME ZONE 'UTC';
\c smart_miner
ALTER TABLE slushpool ADD COLUMN active_users INT NOT NULL;
ALTER TABLE slushpool ADD COLUMN active_workers INT NOT NULL;
