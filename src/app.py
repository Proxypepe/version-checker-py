import signal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rocketry import Rocketry
from prometheus_client import make_asgi_app

from version_checker_service import VersionCheckerService
from config import logger
import uvicorn
import asyncio




app = FastAPI()
service = VersionCheckerService()
scheduler = Rocketry(config={
    'task_execution': 'async',
    'silence_task_logging': False,
})


class Server(uvicorn.Server):
    """
    Customized uvicorn.Server
    """
    def handle_exit(self, sig: int, frame) -> None:
        scheduler.session.shut_down()
        return super().handle_exit(sig, frame)


@scheduler.task('daily')
def run_checks():
    service.check_versions()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/metrics', make_asgi_app(service.metrics.registry))

@app.on_event("startup")
def startup_event():
    # Запуск фоновой проверки версий
    # app_rocketry.run()
    pass


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get('/run')
def run():
    service.check_versions()
    return {"status": "ok"}

@app.post("/reload")
def reload_config():
    if service.reload_config():
        logger.info('Configuration reloaded')
        return {"status": "config reloaded"}
    raise HTTPException(status_code=500, detail="Config reload failed")

def handle_shutdown(signum, frame):
    logger.info("Shutting down...")

async def main():
    server = Server(config=uvicorn.Config(app, workers=2, loop="asyncio", host='0.0.0.0', port=8000))

    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(scheduler.serve())

    await asyncio.wait([sched, api])

if __name__ == "__main__":
    asyncio.run(main())
    # print(service.registry_client.get_available_versions('keycloak/keycloak-operator', 'quay.io'))
    # print(service.k8s_client.get_pod_images(['default']))
    # service.check_versions()
    # print(service.registry_client.get_latest_version('prometheus/node-exporter', 'quay.io', 'v1.9.0'))