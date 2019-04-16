class BiObject:
    """Abstract class that store a data metadata"""
    def __init__(self):
        self._objectname = "BiObject"           

    def display(self):
        print('BiObjectName: ' + self._objectname)
        print('----------------------')
        