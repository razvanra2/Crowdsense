from threading import *
 
class ReusableBarrier():
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.count_threads1 = [self.num_threads]
        self.count_threads2 = [self.num_threads]
        self.count_lock = Lock()                 # protejam accesarea/modificarea contoarelor
        self.threads_sem1 = Semaphore(0)         # blocam thread-urile in prima etapa
        self.threads_sem2 = Semaphore(0)         # blocam thread-urile in a doua etapa
 
    def wait(self):
        self.phase(self.count_threads1, self.threads_sem1)
        self.phase(self.count_threads2, self.threads_sem2)
 
    def phase(self, count_threads, threads_sem):
        with self.count_lock:
            count_threads[0] -= 1
            if count_threads[0] == 0:            # a ajuns la bariera si ultimul thread
                for i in range(self.num_threads):
                    threads_sem.release()        # incrementarea semaforului va debloca num_threads thread-uri
                count_threads[0] = self.num_threads  # reseteaza contorul
        threads_sem.acquire()                    # num_threads-1 threaduri se blocheaza aici
                                                 # contorul semaforului se decrementeaza de num_threads ori