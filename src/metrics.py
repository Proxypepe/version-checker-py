from prometheus_client import Gauge, CollectorRegistry


class MetricsCollector:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.metrics = {
            "version_diff": Gauge(
                "image_version_difference",
                "Difference between current and desired image versions",
                ["image", "namespace", "pod", "current", "desired", "latest"],
                registry=self.registry
            ),
            "version_status": Gauge(
                "image_version_status",
                "Status of image version (0=ok, 1, 2=warning, 3=critical)",
                ["image", "namespace", "pod", "current", "desired", "latest"],
                registry=self.registry
            )
        }

    def update(self, image, desired_tag: str, latest_version: str | None, status: dict):
        labels = {
            "image": image.full_name,
            "namespace": image.namespace,
            "pod": image.pod_name,
            "current": image.tag,
            "desired": desired_tag,
            "latest": latest_version
        }
        
        self.metrics["version_diff"].labels(**labels).set(status["major_diff"])
        
        status_value = 0  # OK
        if status['major_diff']  == -1:
            status_value = 2
        elif status['major_diff'] < -1:
            status_value = 3  # Critical
        elif status["status"] == "minor":
            status_value = 1  # Warning
        self.metrics["version_status"].labels(**labels).set(status_value)
    
    # def get_metrics(self):
    #     return make_asgi_app(self.registry)
        # return generate_latest(self.registry)
