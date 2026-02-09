import logging
from tornado import web, ioloop

from .auth import Handshake

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger(__name__)

class HealthCheck(web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        self.set_status(200)
        self.finish("Ping received...")

class Authenticate(web.RequestHandler):
    def initialize(self):
        self.handshake = None

    def get(self):
        log.info(f"headers: {self.request.headers}")
        signature = self.request.headers.get("signature", None)
        log.info(f"signature: {signature}")
        input_msg = self.request.headers.get("input_msg", None)
        log.info(f"input message: {input_msg}")

        if not any([signature, input_msg]):
            self.set_status(400)
            self.write({"status": "missing headers"})
            return
        self.handshake = Handshake(signature=signature, vamessage=input_msg)
        status = self.handshake.validate_signature()
        if status:
            log.info(f"success ::) you are allowed to push your changes to server")
            self.set_status(200)
            self.write({"status": "allowed"})
        else:
            log.info(f"Failed ::( you are not allowed to push your changes to server")
            self.set_status(403)
            self.write({"status": "forbidden"})

    def post(self):
        log.info(f"storing public key to the authentication server")
        body = self.request.files.get("upload")[0].get("body")
        log.info(f"Signature body: {body}")

        with open(file="/key.verification/PublicKeyStore/pu-key.pem", mode="wb") as pufile:
            pufile.write(body)

        pufile.close()

        log.info(f"stored public key to the authentication server")
        self.set_status(200)
        self.write({"status": "success"})

def make_app():
    return web.Application(
        [
            (r"/get/health", HealthCheck),
            (r"/post/store-pu-key", Authenticate),
            (r"/get/auth-pu-key", Authenticate)
        ]
    )

def main():
    try:
        app = make_app()
        app.listen(port=8080, address="0.0.0.0")
        ioloop.IOLoop.current().start()
        log.info("Server is listening on port 8080")
    except Exception as e:
        log.error(f"Problem: {str(e)}")

if __name__ == "__main__":
    main()
