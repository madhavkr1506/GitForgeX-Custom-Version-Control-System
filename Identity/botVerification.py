import subprocess
import logging

class Verification:
    def __init__(self, verify_bot : bool):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        self.log = logging.getLogger(__name__)

        self.verify_bot = verify_bot

    def verify_robot_identity(self):
        try:
            if self.verify_bot:
                cmd = ["whoami"]
                response = subprocess.run(args=cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if response.returncode == 0:
                    print(f"response: {response.stdout.strip()}")
                    if response.stdout.strip().decode("UTF-8") == "bot":
                        self.log.info(f"bot identity is verified. bot is active...")
                        return 0
                    else:
                        self.log.warning(f"identity failed! {response.stdout.strip()} is active...")
                        return 1
                else:
                    self.log.warning(f"response returncode: {response.returncode}")
                    return 1
            else:
                self.log.warning(f"bot verification is not required. skipping bot verification...")
                return 0   
        except Exception as e:
            self.log.error(f"problem.verify_robot_identity: {str(e)}")
            return 1