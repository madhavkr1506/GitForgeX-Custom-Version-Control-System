import subprocess

class Verification:
    def __init__(self, verify_bot : bool):
        self.verify_bot = verify_bot

    def verify_robot_identity(self):
        try:
            if self.verify_bot:
                cmd = ["whoami"]
                response = subprocess.run(args=cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if response.returncode == 0:
                    print(f"response: {response.stdout.strip()}")
                    if response.stdout.strip().decode("UTF-8") == "bot":
                        return {
                            "message": "identity verified. bot is active...",
                            "status": "success" 
                        }
                    else:
                        return {
                            "message": f"identity failed! {response.stdout.strip()} is active...",
                            "status" : "failed"
                        }
                else:
                    return {
                        "message": f"response returncode: {response.returncode}",
                        "status": "failed"  
                    }    
            else:
                return{
                    "message": "skipped bot verification",
                    "status": "success" 
                }        
        except Exception as e:
            return {
                "message": f"identity verification failed: {str(e)}",
                "status": "failed"
            }