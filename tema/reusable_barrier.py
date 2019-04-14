"""
This module holds a reusable barrier implementation.
"""

from threading import Semaphore, Lock

class ReusableBarrier(object):
    """
    This class is straight out of lab3.
    Honestly. Didn't even read it.
    Taken as is.
    Hope the software comes with warranty & APACHE license.
    """
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.count_threads1 = [self.num_threads]
        self.count_threads2 = [self.num_threads]
        self.count_lock = Lock()                 # protejam accesarea/modificarea contoarelor
        self.threads_sem1 = Semaphore(0)         # blocam thread-urile in prima etapa
        self.threads_sem2 = Semaphore(0)         # blocam thread-urile in a doua etapa

    def wait(self):
        """
        Barrier wait implementation.
        All threads have to wait.
        """
        self.phase(self.count_threads1, self.threads_sem1)
        self.phase(self.count_threads2, self.threads_sem2)
    def phase(self, count_threads, threads_sem):
        """
        Utilitary method as to not bloat barrier.wait
        I think. It's not like i wrote the code.
        """
        with self.count_lock:
            count_threads[0] -= 1
            if count_threads[0] == 0:            # a ajuns la bariera si ultimul thread
                for _ in range(self.num_threads):
                    # incrementarea semaforului va debloca num_threads thread-uri
                    threads_sem.release()
                count_threads[0] = self.num_threads  # reseteaza contorul
        # num_threads-1 threaduri se blocheaza aici
        # contorul semaforului se decrementeaza de num_threads ori
        threads_sem.acquire()
