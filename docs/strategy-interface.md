# Strategy Interface Specifications

## The Methods
1. `open`
   
    **Arguments:**
    - Virtual order ID
    - Order ID  
    - List of start triggers that caused this `open`
    - Handle to all useful modules:
        - Logger
        - Virtual orders handler
        - Virtual orders updater
        - Orders DB handler
        - Orders DB updater
        - Mine DB handler
        - Mine DB updater
        - Simulation DB handler
        - Simulation DB updater
        - Virtual order request applier
        - Analyzer
        - Learner
        - Configuration

2. `refresh_state`

3. `reconcile`
   
    **Args:** List of triggers that caused the call to `reconcile`

4. `close`
    **Args:** List of criteria that was met to trigger `close`

5. `status`
    - `pending`
    - `running`
    - `stopped`
    - `lost_track`

6. `should_end`    

## **Strategy Scheduling Request (SSR)**
- **Abstract description:** Defaults to False. Not scheduled as a real request and
  used only as the base class of a real request if True.
- **SSR name**
- **SSR base name** that, if given, will provide values that
  are used anywhere no value is given in this SSR.
- **Package path** to load dynamically
- **Lifecycle info**
    - start time options (OR if more than one is given):
        - **timestamp**: first time this timestamp is passed)
        - **timestamp in [ts<sub>begin</sub>, ts<sub>finish</sub>]**: anytime
          the current timestamp is in the given interval.
        - when a **block** is solved with **duration in [d<sub>low</sub>, d<sub>high</sub>]**
    - end time options (OR if more than one is given):
        - timestamp
        - after `T` seconds since start
        - after `B` new blocks since start
        - strategy determines dynamically
    - execution parameters:
        - **Parallel**: Defaults to False. Schedule a new clone of the request whenever 
          the criteria holds (even if it is already scheduled once).
        - **Repeat**: Defaults to False. Schedule the request 
    again after it ends if its start criteria is met again.
- **Triggers** to call the reconcile method. Possible options are:
    - Every `s` seconds
    - Timestamp `pins` requested during execution (like `s` seconds later, 
      or at timestamp `t`)
    - When a new block is solved
    - Triggers A<sub>1</sub>, ..., A<sub>m</sub> defined in the Analyzer
    - Triggers M<sub>1</sub>, ..., M<sub>n</sub> defined in the Learner
- **Order info**
    - **physical order id:** the id of the real Nicehash order that 
      must be used for the virtual order requests issued by this 
      strategy. Possible options are:
      - `any-available`: any available can be used. If the previous order cannot
    be found after a restart of the program, any other available order
        may be used. Note: the virtual order id does not change.
      - `any-fixed`: any available can be used; but once the order id is set,
    it cannot change and this strategy needs the old order to exist to 
        continue working after a restart. Note: the virtual order id does 
        not change.
      - `ID/order id/`: specific order id value to be used underlying 
    the strategy virtual order requests. Strategy does not work if no orders
        with the given id exist. One example of the value is:
        
        `ID/fsdfs-dfsdf32-dwfsadf-432345634-34234253463423-fsdfsfsf/`
