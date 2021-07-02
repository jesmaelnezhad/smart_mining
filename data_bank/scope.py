from data_bank.orders.driver.realtime_driver import NiceHashRealtimeDriver
from data_bank.orders.driver.simulation_driver import NiceHashSimulationDriver


class RuntimeScopeIdentifier:
    DRIVER = None

    def get_runtime_scope_database_prefix(self):
        pass

    def get_runtime_scope_should_drop_at_first(self):
        pass

    def get_nice_hash_driver(self):
        pass


class RealtimeScopeIdentifier(RuntimeScopeIdentifier):
    def get_runtime_scope_database_prefix(self):
        return ""

    def get_runtime_scope_should_drop_at_first(self):
        return False

    def get_nice_hash_driver(self):
        if self.DRIVER is None:
            self.DRIVER = NiceHashRealtimeDriver()
        return self.DRIVER


class SimulationScopeIdentifier(RuntimeScopeIdentifier):
    def get_runtime_scope_database_prefix(self):
        return "simulation_"

    def get_runtime_scope_should_drop_at_first(self):
        return True

    def get_nice_hash_driver(self):
        if self.DRIVER is None:
            self.DRIVER = NiceHashSimulationDriver()
        return self.DRIVER
