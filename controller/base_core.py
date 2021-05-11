class BaseCore:
    DEFAULT_SHOULD_BE_PROVIDED_ACTIVE_ORDER = True

    def should_be_provided_order(self):
        return self.DEFAULT_SHOULD_BE_PROVIDED_ACTIVE_ORDER

    def get_order_id_to_work_with(self):
        pass