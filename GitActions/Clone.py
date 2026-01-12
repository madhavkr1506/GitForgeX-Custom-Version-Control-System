import os
import platform
import subprocess

class GitClone:
    def __init__(self):
        self.get_cmd = None

    def prepare_get_cmd(self, filehash=None, commithash=None):
        try:
            cmd = [
                "curl",
                "-X",
                "GET",
                "http://localhost:8000/get/92f21be4d8b290637e93c4b9790a03bec823c6e6e218ac7b925c3e6f753fd69a",
                "-o", "./clonedir/testscript2.txt"
            ]
            print(f"command: {cmd}")            
            self.get_cmd = cmd
        except Exception as e:
            raise Exception(str(e))
    
    def validate_input(self, input_dir):
        try:
            for key, value in input_dir.items():
                match key:
                    case "filepath":
                        if platform.system() == "Windows":
                            if os.path.exists(value):
                                return True
                            else:
                                return False
                        else:
                            print(f"OS is not windows")
                            return False

        except Exception as e:
            raise Exception(str(e))

    def clone(self):
        try:
            response = subprocess.run(args=self.get_cmd, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if response.returncode == 0:
                print(f"subprocess output: {response.stdout}")
                return
            print(f"subprocess error: {response.stderr}")
            return
        except Exception as e:
            raise Exception(str(e))
        
if __name__ == "__main__":
    gitclone = GitClone()
    output = gitclone.validate_input({
        "filepath": "D:\\Genome\\GitForgeX\\tracking\\testscript2.txt"
    })
    print(output)
    gitclone.prepare_get_cmd()
    gitclone.clone()