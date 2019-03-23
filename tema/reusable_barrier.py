from threading import Condition

class ReusableBarrier():
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.count_threads = self.num_threads    # contorizeaza numarul de thread-uri ramase
        self.cond = Condition()                  # blocheaza/deblocheaza thread-urile
                                                 # protejeaza modificarea contorului
 
    def wait(self):
        self.cond.acquire()                      # intra in regiunea critica
        self.count_threads -= 1;
        if self.count_threads == 0:
            self.cond.notify_all()               # deblocheaza toate thread-urile
            self.count_threads = self.num_threads    # reseteaza contorul
        else:
            self.cond.wait();                    # blocheaza thread-ul eliberand in acelasi timp lock-ul
        self.cond.release();                     # iese din regiunea critica