class FieldElement:

    def _init_(self, num, prime):
        if num >= prime or num < 0:
            error = 'Num {} not in field range 0 to {}'.format(num, prime -1)
            raise ValueError(error)
        self.num = num
        self.prime = prime
    
    def _repr_(self):
        return 'FieldElement_{} ({})'.format(num, prime - 1)
    
    def _eq_ (self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime