import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
class Handshake:
    def __init__(self, signature : str = None, vamessage : str = None):
        self.signature = signature
        self.signature = bytes.fromhex(self.signature)
        self.vamessage = vamessage
        self.vamessage = bytes.fromhex(self.vamessage)

        self.public_key_store = "/key.verification/PublicKeyStore/pu-key.pem"
        self.public_key = None
        self.adjust_signatures_verification_params()

    def adjust_signatures_verification_params(self):
        self.pupadding = padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
        self.pualgorithm = hashes.SHA256()

    def load_keys(self):
        try:
            if not os.path.exists(self.public_key_store):
                return False
            pem = None
            key = None
            with open(file=self.public_key_store, mode="rb") as pukey:
                pem = pukey.read()
            pukey.close()
            key = serialization.load_pem_public_key(
                data=pem
            )
            self.public_key = key
            key = None
            return True 
        except Exception as e:
            print(f"problem: {str(e)}", flush=True)
    
    def validate_signature(self):
        try:
            if self.signature is None:
                return False
            if self.public_key is None:
                response = self.load_keys()
                if response:
                    self.public_key.verify(
                        signature=self.signature,
                        data=self.vamessage,
                        padding=self.pupadding,
                        algorithm=self.pualgorithm
                    )
                    return True
                else:
                    return False
        except Exception as e:
            print(f"problem: {str(e)}", flush=True)
                
