import json
import time
from tornado import web
from tornado import ioloop

from Identity.botVerification import Verification
from Actions.botAction import *

class MainHandler(web.RequestHandler):
    def initialize(self):
        self.robot = BotHandler()

    def get(self, hash):
        verification = Verification(verify_bot=True)
        response = verification.verify_robot_identity()
        if response.get("status") == "success":
            print(f"success verification: {response}", flush=True)
            filename = f"./snapshots/{hash}"
            data = None
            with open(file=filename, mode="rb") as file:
                data = file.read()

            if data is not None:
                self.write(data)
        else:
            print(f"failed verification: {response}", flush=True)
            self.write(response)

    def post(self):
        verification = Verification(verify_bot=True)
        response = verification.verify_robot_identity()
        if response.get("status") == "success":
            print(f"success verification: {response}", flush=True)
            commit_hash = self.get_body_argument("commit_hash")
            print(f"commit hash: {commit_hash}", flush=True)
            filehash = self.get_body_argument("filehash")
            print(f"filehash: {filehash}", flush=True)
            commitmsg = self.get_body_argument("commitmsg")
            print(f"commit message: {commitmsg}", flush=True)
            filepath = f"./snapshots/{filehash}"
            print(f"filepath: {filepath}", flush=True)

            body = self.request.files.get("upload")[0].get("body")
            if body is not None:
                with open(file=filepath, mode="wb") as f:
                    f.write(body)
                response = {
                    "message": f"{filepath} has been saved successfully",
                    "status": "success"
                }
                self.robot.insert_indb(commithash=commit_hash, fileshash=filehash, commitmsg=commitmsg)
                self.write(json.dumps(response, indent=4))
            else:
                response = {
                    "message": f"{filepath} is not saved successfully as body is None",
                    "status": "failure"
                }
                self.write(json.dumps(response, indent=4))
            
        else:
            print(f"failed verification: {response}", flush=True)
            self.write(response)

class HandshakeHandler(web.RequestHandler):
    def initialize(self):
        self.headers = self.request.headers
        print(self.headers, flush=True)

        signature = self.headers.get("signatures", None)
        vamessage = self.headers.get("valmessage", None)
        print({
            "server received": {
                "signature": signature,
                "vamessage": vamessage
            }
        }, flush=True)
        if signature is not None and vamessage is not None:
            self.handshake = Handshake(signature=signature, vamessage=vamessage)

    def get(self):
        response = self.handshake.validate_signature()
        self.write(response)

    def post(self):
        upload = self.request.files.get("upload")
        print(
            {
                "upload": upload 
            }, flush=True
        )
        filebody = upload[0].get("body")
        print(
            {
                "filebody": filebody
            }, flush=True
        )
        with open(file="/src/app/.git/Keystores/publickey.pem", mode="wb") as pufile:
            pufile.write(filebody)
        
        pufile.close()

        self.write(
            {
                "response": "public key is store on server",
                "b_status": "success"
            }
        )

    
class TestHandler(web.RequestHandler):
    def initialize(self):
        self.verification = Verification(verify_bot=True)
        self.dbconnection = DBConnection()


    def get(self):
        response = self.verification.verify_robot_identity()
        if response.get("status") == "success":
            print(f"success verification: {response}", flush=True)
            
            response = self.dbconnection.test_session_reliablity()

            print(f"database test response: {response}", flush=True)
            self.set_status(200)
            self.finish(f"ping received...")
        else:
            print(f"failed verification: {response}", flush=True)
            self.write(response)

def make_app():
    return web.Application([
        (r"/", TestHandler),
        (r"/get/([a-zA-Z0-9]+)", MainHandler),
        (r"/post", MainHandler),
        (r"/handshake", HandshakeHandler),
        (r"/store-pu-key", HandshakeHandler)
    ])

def main():
    try:
        app = make_app()
        app.listen(port=8000, address="0.0.0.0")
        ioloop.IOLoop.current().start()
        response = {
            "message": "server is listening on port 8000",
            "status": "success"
        }
        print(json.dumps(response, indent=4))

    except Exception as e:
        response = {
            "message": f"{str(e)}",
            "status": "failure"
        }
        print(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()