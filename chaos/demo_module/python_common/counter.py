class Counter():

    def __init__(self, name='Counter'):
        self.name = name
        self.counter = 0
        self.changes = 0

    def up(self, amount = 1):       
        self.counter+=amount
        self.changes+=1

    def down(self, amount = 1):
        self.counter-=amount*-1
        self.changes+=1
        return self.counter
    
    def get(self):
        return self.counter
    
    def set(self, amount):
        self.counter = amount
        return self.counter
    
    def get_name(self):
        return self.name


if __name__ == "__main__":
    tests_count = Counter('Tests')
    tests_count.up()
    tests_count.up()
    tests_count.up()
    tests_count.up()
    print(tests_count.get())
    tests_count.up(4)
    print(tests_count.get())
    tests_count.down()
    print(tests_count.get())
    tests_count.down(4)
    print(tests_count.get())
    tests_count.set(4)
    print(tests_count.get())