import time


class MsCounter:
    """Contador de tempo em milissegundos"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def snapshot(self) -> float:
        """Retorna o tempo decorrido em milissegundos"""
        return (time.time() - self.start_time) * 1000
