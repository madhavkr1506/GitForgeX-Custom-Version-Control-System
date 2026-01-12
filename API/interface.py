import json
import time
from tornado import web
from tornado import ioloop

from Identity.botVerification import Verification
from Actions.botAction import *

class MainHandler(web.RequestHandler):
    def initialize(self):
        self.robot = BotHandler()
        self.filehash = None
        self.commit_hash = None

    def get(self):
        verification = Verification(verify_bot=True)
        response = verification.verify_robot_identity()
        if response.get("status") == "success":
            print(f"success verification: {response}", flush=True)
            filehash = self.get_body_argument(name="filehash", default="not found", strip=True)
            if filehash == "not found":
                print(f"filehash is not given. using commit hash", flush=True)
            self.filehash = filehash
            commit_hash = self.get_body_argument(name="commit_hash", default="not found", strip=True)
            if commit_hash == "not found":
                print(f"commit hash is not given", flush=True)
            self.commit_hash = commit_hash
            if len(self.filehash) == 0 and len(self.commit_hash) == 0:
                self.write(chunk={
                    "response": "invalid parameter. get operation failed",
                    "b_status": "failed"
                })
                return

            rows = self.robot.select_fromdb(commithash=commit_hash)
            if rows:
                for row in rows:
                    filehash = row[0][0]
                    filepath = f"./snapshots/{filehash}"
                    if os.path.exists(path=filepath):
                        data = None
                        with open(file=filepath, mode="rb") as file:
                            data = file.read()
                        if data:
                            self.write(data)
                    else:
                        self.set_status(404)
                        self.finish("resource not found")
                        return
            else:
                self.set_status(404)
                self.finish("no commit history found")
                return
            self.finish()
        else:
            print(f"failed verification: {response}", flush=True)
            self.write(response)

    def post(self):
        verification = Verification(verify_bot=True)
        response = verification.verify_robot_identity()
        if response.get("status") == "success":
            print(f"success verification: {response}", flush=True)
            commithash = self.get_body_argument("commit_hash")
            filehash = self.get_body_argument("filehash")
            commitmsg = self.get_body_argument("commitmsg")
            filepath = f"./snapshots/{filehash}"
            print(
                json.dumps(
                    {
                        "commit hash": f"{commithash}",
                        "file hash": f"{filehash}",
                        "commit message": f"{commitmsg}",
                        "remote file path": f"{filepath}"
                    }, indent=4, sort_keys=True
                ), flush=True
            )

            body = self.request.files.get("upload")[0].get("body")
            if body is not None:
                with open(file=filepath, mode="wb") as f:
                    f.write(body)
                response = {
                    "message": f"{filepath} has been saved successfully",
                    "status": "success"
                }
                self.robot.insert_indb(commithash=commithash, fileshash=filehash, commitmsg=commitmsg)
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
            json.dumps(
                {
                    "response": "congratulation::) public key is store on server and ready to validate signature",
                    "b_status": "success"
                }, indent=4
            ),
        )

    
class TestHandler(web.RequestHandler):
    def initialize(self):
        self.verification = Verification(verify_bot=True)
        self.dbconnection = DBConnection()


    def get(self):
        response = self.verification.verify_robot_identity()
        if response.get("status") == "success":
            print(
                json.dumps(
                    {
                        "response": f"verification success: {response}"
                    }
                ), flush=True
            )
            
            response = self.dbconnection.test_session_reliablity()

            print(
                json.dumps(
                    {
                        "response": f"session connection : {response}"
                    }
                )
                , flush=True)
            self.set_status(200)
            self.finish(f"ping received...")
        else:
            print(
                json.dumps(
                    {
                        "response": f"verification failed: {response}"
                    }
                )
                , flush=True)
            self.write(response)

def make_app():
    return web.Application([
        (r"/", TestHandler),
        (r"/get", MainHandler),
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
        print(json.dumps(response, indent=4), flush=True)

    except Exception as e:
        response = {
            "message": f"{str(e)}",
            "status": "failure"
        }
        print(json.dumps(response, indent=4), flush=True)


if __name__ == "__main__":
    main()