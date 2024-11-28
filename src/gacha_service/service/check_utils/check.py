
class Checker:
    mock_check = None

    def __init__(self,mock_check):
        self.mock_check = mock_check

    def tux(self):
        if self.mock_check:
            return True 
        else:
            return True
    
    def user(self):
        if self.mock_check:
            return True 
        else:
            return True
    
    def admin(self):
        if self.mock_check:
            return True 
        else:
            return True