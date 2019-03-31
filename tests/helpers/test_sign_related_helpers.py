from masonite.auth import Sign
from masonite.helpers.sign import sign, encrypt, unsign, decrypt

class TestSignRelatedHelpers:
    
    def setup_method(self):
        self.sign = Sign()
        self.word = 'uyfgeruyre'

    def test_sign_helper(self):
        assert sign(self.word) == self.sign.sign(self.word)

    def test_encrypt_helper(self):
        assert encrypt(self.word) == self.sign.sign(self.word) 

    def test_unsign_helper(self):
        assert unsign(self.word) == self.sign.unsign(self.word) 

    def test_decrypt_helper(self):
        assert decrypt(self.word) == self.sign.unsign(self.word) 