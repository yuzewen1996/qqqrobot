from abc import ABC, abstractmethod
from core.exchange import Exchange

class BaseStrategy(ABC):
    def __init__(self, exchange: Exchange, config: dict):
        self.exchange = exchange
        self.config = config
        self.name = "BaseStrategy"

    @abstractmethod
    def run(self):
        """执行策略逻辑"""
        pass
