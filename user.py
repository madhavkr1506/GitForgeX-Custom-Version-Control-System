import os
import sys
import json 
import subprocess

from pathlib import *
from Logging import *
from Handshake import *
from GitActions import *

class UserAction:
    def __init__(self):
        self.log = PrintLog()
        self.log = self.log.log

        self.user_action = None
        self.check_gitactions_path_status = False

        self.server_start_status = False

    def run(self):
        steps = [self.check_gitactions_path, self.start_container_spin]
        for step in steps:
            step()

    def start_container_spin(self):
        try:
            cmd = [
                "docker-compose", 
                "up", "-d"
            ]
            self.log.info(f"command prepared to start server: {cmd}")
            response = subprocess.run(args=cmd, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if response.returncode == 0:
                self.log.info(json.dumps({
                    "response" : "server is listening at port 8000",
                    "u_status" : "success"
                }, indent=4))
                self.server_start_status = True
                return
            self.log(json.dumps({
                "response" : f"failed to start server: {str(e)}",
                "u_status" : f"failed"
            }, indent=4))
            return

        except Exception as e:
            self.log.error(json.dumps({
                "response" : f"failed to start server (docker container): {str(e)}",
                "u_status" : "failed"
            }, indent=4))
    
    def stop_container_spin(self):
        try:
            cmd = [
                "docker-compose", 
                "down", "--volumes"
            ]
            self.log.info(json.dumps({
                "response" : f"stop running container\ncommand: {cmd}",
                "u_status" : "success" 
            }, indent=4))
            response = subprocess.run(args=cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if response.returncode == 0:
                self.log.info(json.dumps({
                    "response": f"standard ouput: {response.stdout}",
                    "u_status" : "success"
                }, indent=4))
                return
            self.log.info(json.dumps({
                    "response": f"standard error: {response.stderr}",
                    "u_status" : "failed"
                }, indent=4))
        except Exception as e:
            self.log.error(json.dumps({
                "response" : f"failed to stop spinning container: {str(e)}",
                "u_status" : 'failed'
            }, indent=4))

    def check_gitactions_path(self):
        if os.path.exists("./GitActions/"):
            self.log.info(json.dumps({
                "response": "git actions are defined",
                "u_status" : "success"
            }, indent=4))
            self.check_gitactions_path_status = True
    def get_user_action(self):
        print(f"input user action: ", end="\t", flush=True)
        input_ = sys.stdin.readline().strip()
        self.set_user_action(user_action=input_)

    def set_user_action(self, user_action):
        self.user_action = user_action

    def process_user_action(self):
        try:
            if self.server_start_status == False:
                return
            while True:
                self.get_user_action()
                match self.user_action:
                    case "add":
                        AddActions(path=Path("./Tracking"))
                    case "stage":
                        Staging().run()
                    case "commit":
                        Commit().run()
                    case "push":
                        Push().run()
                    case "clone":
                        GitClone()
                    case "cherry-pick":
                        CherryPickCommit().run()
                    case "revert":
                        pass
                    case "reset":
                        GitReset().run()
                    case "handshake":
                        KeyGeneration()
                    case "exit":
                        self.stop_container_spin()
                        break
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.log.error(json.dumps({
                "message" : f"process action failed: {str(e)}",
                "status" : "failed"
            }, indent=4))

if __name__ == "__main__":
    u_action = UserAction()
    u_action.run()
    u_action.process_user_action()