import os
import sys
import json
import subprocess
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

class KeyGeneration:
    def __init__(self):
        self.privatekey = None
        self.public_key = None

        self.privatekey_store = None
        self.public_key_store = None

        self.signatures = None
        self.handshake_digest = None
        self.handshake_digest_hex = None

    def run(self):
        print(f"input password: ", end="\t", flush=True)
        self.password = str(sys.stdin.readline()).strip()
        self.password = self.password.encode("UTF-8")
        print(f"password entered: {self.password}")

        steps = [self.adjust_private_key_params, self.adjust_private_bytes_params, self.adjust_public_bytes_params, self.adjust_private_key_sign_params]

        for step in steps:
            step()

        self.call_keystores()

    def adjust_private_key_params(self):
        self.public_exponent = 65537
        self.key_size = 3048

    def adjust_private_bytes_params(self):
        self.prencoding = serialization.Encoding.PEM
        self.prformat = serialization.PrivateFormat.PKCS8
        self.prencryption_algorithm = serialization.BestAvailableEncryption(password=self.password)

    def adjust_public_bytes_params(self):
        self.puencoding = serialization.Encoding.PEM
        self.puformat = serialization.PublicFormat.SubjectPublicKeyInfo # Key structure / format (public)

    def adjust_private_key_sign_params(self):
        self.prpadding = padding.PSS(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        )
        self.pralgorithm = hashes.SHA256()

    def getnerate_keys(self):
        try:
            if self.privatekey is not None and self.public_key is not None:
                return
            key = rsa.generate_private_key(
                public_exponent=self.public_exponent,
                key_size=self.key_size
            )
            self.privatekey = key

            key = None

            if self.privatekey is not None:
                key = self.privatekey.public_key()
                self.public_key = key

            key = None
            print({
                "response": "private key and public is generated",
                "r_status": "success"
            }, flush=True)
        except Exception as e:
            raise Exception(
                {
                    "response": f"failed to generate public key and private key: {str(e)}",
                    "r_status": "failed"
                }
            )
        

    def call_keystores(self):
        try:
            self.public_key_store = "./Keystores/public_key.pem"
            self.privatekey_store = "./Keystores/private_key.pem"
            if os.path.exists(self.privatekey_store) and os.path.exists(self.public_key_store):
                return
            
            if self.privatekey is None and self.public_key is None:
                self.getnerate_keys()

            pem = None
            pem = self.privatekey.private_bytes(
                encoding=self.prencoding,
                format=self.prformat,
                encryption_algorithm=self.prencryption_algorithm
            )
            
            with open(file=self.privatekey_store, mode="wb") as prfile:
                prfile.write(pem)
            prfile.close()
            pem = None

            pem = self.public_key.public_bytes(
                encoding=self.puencoding,
                format=self.puformat,
            )

            with open(file=self.public_key_store, mode="wb") as pufile:
                pufile.write(pem)
            
            pufile.close()

            pem = None

            print({
                "response": "private key and public key is stored inside keystores",
                "r_status": "success"
            }, flush=True)
            
        except Exception as e:
            raise Exception(
                {
                    "response": f"private key and public is not stored: {str(e)}",
                    "r_status": "failed"
                }
            )
        
    def load_keys(self):
        try:
            if not os.path.exists(self.privatekey_store) and not os.path.exists(self.public_key_store):
                self.call_keystores()

            pem = None
            key = None

            with open(file=self.privatekey_store, mode="rb") as prfile:
                pem = prfile.read()
            
            prfile.close()

            key = serialization.load_pem_private_key(
                data=pem, password=self.password
            )

            self.privatekey = key

            pem = None
            key = None

            with open(file=self.public_key_store, mode="rb") as pufile:
                pem = pufile.read()

            pufile.close()

            key = serialization.load_pem_public_key(
                data=pem
            )

            self.public_key = key

            pem = None
            key = None

            print(
                {
                    "response": "private key and public key are loaded",
                    "r_status": "success"
                }
                ,flush=True)
        except Exception as e:
            raise Exception(
                {
                    "response": f"public key and private key are not loaded: {str(e)}",
                    "r_status": "failed"
                }
            )
        
    def build_hashdigest(self, message : str):
        hash_ = hashes.Hash(algorithm=hashes.SHA256())
        hash_.update(message.encode("UTF-8"))
        hashdigest_ =hash_.finalize()
        return hashdigest_
        
    def put_privatekey_signature(self, handshake_msg : str):
        try:
            if self.privatekey is None and self.public_key is None:
                self.load_keys()

            hashdigest_ = self.build_hashdigest(message=handshake_msg)
            self.handshake_digest = hashdigest_
            self.handshake_digest_hex = self.handshake_digest.hex()

            self.signatures = self.privatekey.sign(
                data=self.handshake_digest,
                padding=self.prpadding,
                algorithm=self.pralgorithm
            )
            self.signatures = self.signatures.hex()
            print({
                "response": "signature added over handshake message",
                "r_status": "success"
            }, flush=True)
        except Exception as e:
            raise Exception(
                {
                    "response": f"failed to put signature on data: {str(e)}",
                    "r_status": "failed"
                }
            )
        
    def store_publickey_on_server(self):
        try:
            if not os.path.exists(path=self.public_key_store):
                print(
                    {
                        "response": "public key store is missing",
                        "r_status": "failed"
                    },
                    flush=True
                )
                self.call_keystores()

            cmd = None

            def prepare_cmd():
                cmd_ = [
                    "curl", 
                    "-X", "POST", 
                    "http://localhost:8000/store-pu-key",
                    "-F", f"upload=@{self.public_key_store}"
                ]
                return cmd_
            
            cmd = prepare_cmd()

            print(f"storing public key on server: {cmd}")

            response = subprocess.run(args=cmd, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if response.returncode == 0:
                response, r_status = self.phrase_server_response(response.stdout)

                if r_status:
                    print(
                        {
                            "response": f"reading response from server: {response}",
                            "r_status": "success"
                        }
                    )
                if not r_status:
                    print(
                        {
                            "response": f"reading response from server: {response}",
                            "r_status": "failed"
                        }
                    )
            else:
                print(
                    {
                        "response": f"failed in reading response from server: {response.stderr}",
                        "r_status": "failed"
                    }
                )


        except Exception as e:
            raise Exception(
                {
                    "response": f"public key is not stored on server: {str(e)}",
                    "r_status": "failed"
                }
            )
        
    def do_handshake(self):
        try:
            print(f"input handshake message: ", end="\t", flush=True)
            handshake_msg = sys.stdin.readline().strip()
            print(f"handshake message entered: {handshake_msg}")

            self.put_privatekey_signature(handshake_msg=handshake_msg)

            def prepare_cmd():
                cmd = [
                    "curl",
                    "-X", "GET",
                    "-H", f"signatures: {self.signatures}",
                    "-H", f"valmessage: {self.handshake_digest.hex()}",
                    "http://localhost:8000/handshake"
                ]

                return cmd
            
            cmd = None
            cmd = prepare_cmd()

            response = None
            print(f"handshake command: {cmd}")
            response = subprocess.run(args=cmd, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if response.returncode == 0:
                
                response, r_status = self.phrase_server_response(response.stdout)
                if r_status:
                    print(
                        {
                            "response": f"reading response from server: {response}",
                            "r_status": "success"
                        }
                    )
                if not r_status:
                    print(
                        {
                            "response": f"reading response from server: {response}",
                            "r_status": "failed"
                        }
                    )
                    self.store_publickey_on_server()
            else:
                print(
                    {
                        "response": f"failed in reading response from server: {response.stderr}",
                        "r_status": "failed"
                    }
                )

        except Exception as e:
            raise Exception({
                "response": f"handshake failed with server: {str(e)}",
                "r_status": "failed"  
            })
        
    
    def phrase_server_response(self, server_response):
        try:
            response = None
            r_status = None
            if not server_response:
                print(
                    {
                        "response": "server response is None",
                        "r_status": "failed"
                    }, flush=True
                )
                return
            else:
                if isinstance(server_response, str):
                    server_response = json.loads(server_response)
                response = server_response.get("response")
                r_status = True if server_response.get("b_status") == "success".lower() else False

            return response, r_status

        except Exception as e:
            raise Exception(
                {
                    "response": f"failed to read response from server: {str(e)}",
                    "r_status": "success"
                }
            )