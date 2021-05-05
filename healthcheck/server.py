from http.server import BaseHTTPRequestHandler, HTTPServer

from configuration import EXECUTION_CONFIGS
from healthcheck import get_health_check_watcher
from utility.log import logger


class HealthCheckServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        health_check_watcher = get_health_check_watcher()
        health_check_watcher.reset_silent_cycles_count()


def start_healthcheck_server():
    logger("healthcheck/server").info("Starting the server.")
    server_info = (EXECUTION_CONFIGS.healthcheck_listen_address, EXECUTION_CONFIGS.healthcheck_listen_port)
    httpd = HTTPServer(server_info, HealthCheckServer)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logger("healthcheck/server").info("Closing the server.")
        httpd.server_close()
