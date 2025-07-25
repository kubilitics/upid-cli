
class Plugin:
    def __init__(self):
        self.name = "test_plugin"
    
    def on_optimization_completed(self, data):
        print(f"Plugin {self.name} received optimization data: {data}")
        return {"status": "processed", "plugin": self.name}
    
    def on_cluster_health_changed(self, data):
        print(f"Plugin {self.name} received health data: {data}")
        return {"status": "processed", "plugin": self.name}
