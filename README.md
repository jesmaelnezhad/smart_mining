# smart_mining

## Program execution mode
1. **Realtime:** a standalone package (except it uses PostgreSQL) whose main job is to control one or more 
   `virtual order(s)`, each of which uses the single real provisioned `active order`
   in NiceHash to execute the `play` of a `strategy`.
1. **Simulation:** a package to simulate the realtime execution on a time interval in 
   the past with accelerated speed. This mode uses a mock written for the real nice hash
   API handler classes.
1. **Healtcheck:** an HTTP server that is always listening for the realtime controller 
   to poke it; and if it doesn't receive a request for long enough, it `panic`s and 
   takes down the limit/price to zero on the active order being used.
