from masonite.auth import Sign
from masonite.helpers.sign import sign, encrypt, unsign, decrypt

class TestSignRelatedHelpers:
    
    def setup_method(self):
        self.sign = Sign()
        self.word = b'uyfgeruyre'

    def test_same_methods(self):
        assert sign == self.sign.sign