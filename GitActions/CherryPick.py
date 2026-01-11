import json
import subprocess
class PickCommit:
    def __init__(self):
        self.get_commitcmd = None

    def run(self):
        steps = [lambda : self.get_commit(filehash="035b58e5e8a7e4253f205ddd402b63f9bf697ae787cec01a956b4bbe69c807ad", outputpath="Get commits\\testscript2.txt"), self.execute_getcommitcmd]
        for step in steps:
            step()


    def get_commit(self, filehash=None, commithash=None, outputpath = None):
        try:
            cmd = [
                "curl",
                "-X",
                "GET",
                f"http://localhost:8000/get/{filehash}",
                "-o", f"{outputpath}"
            ]
            print(
                json.dumps(
                    {
                        "command": cmd
                    }, indent=4
                )
            )
            self.get_commitcmd = cmd
        except Exception as e:
            print(
                json.dumps(
                    {
                        "error": f"get commit command is not prepared: {str(e)}"
                    }, indent=4
                )
            )

    def execute_getcommitcmd(self):
        try:
            response = subprocess.run(args=self.get_commitcmd, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if response.returncode == 0:
                print(
                    json.dumps(
                        {
                            "response": f"{response.stdout}",
                            "u_status": "success"
                        }
                    )
                )
            else:
                print(
                    json.dumps(
                        {
                            "response": f"{response.stderr}",
                            "u_status": "failed"
                        }
                    )
                )

        except Exception as e:
            print(
                json.dumps(
                    {
                        "error": f"failed to execute command: {str(e)}"
                    }, indent=4
                )
            )