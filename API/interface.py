import json
import time
from tornado import web
from tornado import ioloop

from Identity.botVerification import Verification
from Actions.botAction import *

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger(__name__)

class MainHandler(web.RequestHandler):
    def initialize(self):
        self.robot = BotHandler()
        self.filehash = None
        self.commit_hash = None

    def get(self):
        verification = Verification(verify_bot=True)
        code = verification.verify_robot_identity()
        if code == 0:
            log.info(f"successful verification. bot identity is verified")
            filehash = self.get_body_argument(name="filehash", default="not found", strip=True)
            if filehash == "not found":
                log.info(f"filehash is not given. using commit hash")
            self.filehash = filehash
            commit_hash = self.get_body_argument(name="commit_hash", default="not found", strip=True)
            if commit_hash == "not found":
                log.info(f"commit hash is not given")
            self.commit_hash = commit_hash
            if len(self.filehash) == 0 and len(self.commit_hash) == 0:
                self.write(chunk={"status": 1})
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
            log.warning(f"bot identity is not verified")

    def post(self):
        verification = Verification(verify_bot=True)
        code = verification.verify_robot_identity()
        if code == 0:
            log.info(f"successful verification. bot identity is verified")
            commithash = self.get_body_argument("commit_hash")
            filehash = self.get_body_argument("filehash")
            commitmsg = self.get_body_argument("commitmsg")
            filepath = f"./snapshots/{filehash}"
            log.info(f"filepath={filepath}\tfilehash={filehash}\tcommit hash={commithash}")
            body = self.request.files.get("upload")[0].get("body")
            if body is not None:
                with open(file=filepath, mode="wb") as f:
                    f.write(body)
                self.robot.insert_indb(commithash=commithash, fileshash=filehash, commitmsg=commitmsg)
                self.write({"status": 0})
            else:
                log.warning(f"fetched body is none")
                self.write({"status": 1})
        else:
            log.warning(f"bot identity is not verified")
    
class TestHandler(web.RequestHandler):
    def initialize(self):
        self.verification = Verification(verify_bot=True)
        self.dbconnection = DBConnection()


    def get(self):
        code = self.verification.verify_robot_identity()
        if code == 0:
            log.info(f"bot verified")
            code = self.dbconnection.test_session_reliablity()
            if code == 0:
                log.info(f"database connection is established")
                self.set_status(200)
                self.finish(f"ping received...")
            else:
                log.warning(f"database connection is not established")
                self.set_status(403)
                self.finish(f"ping not received...")
        else:
            log.warning(f"bot unverified")
            self.set_status(403)

def make_app():
    return web.Application([
        (r"/", TestHandler),
        (r"/get", MainHandler),
        (r"/post", MainHandler)
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