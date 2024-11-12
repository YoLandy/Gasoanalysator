class GasReader():
    def __init__(self) -> None:
        self.current_step = ''

    def get_data(self):
        self.current_step = 'asking_data'

    def set_active(self):
        self.current_step = 'set_active'

    def recieve(self, answer):
        if self.current_step == 'asking_data':
            if answer == 'error':
                #send activate
                self.current_step = 'activating'
                pass
            if answer == 'data':
                #operate data and send
                pass
            
    
