from numba import cuda
import numpy as np


class Test :
    
    @cuda.autojit
    def saxpy(self, a, b, c):
        # Determine our unique global thread ID, so we know which element to process
        tid = cuda.blockIdx.x * cuda.blockDim.x + cuda.threadIdx.x;
    
        if ( tid < c.size ): # Make sure we don't do more work than we have data!
            c[tid] = 2 * a[0] + b[tid];

    def main(self):
        N = 2048 * 2048
    
        # Allocate host memory arrays
        a = np.empty(N)
        b = np.empty(N)
        c = np.empty(N)
    
        # Initialize host memory
        a.fill(2)
        b.fill(1)
        c.fill(0)
    
        # Allocate and copy GPU/device memory
    #     d_a = cuda.to_device(a)
    #     d_b = cuda.to_device(b)
    #     d_c = cuda.to_device(c)
        
        threads_per_block = 128
        number_of_blocks = (N / 128) + 1
    
        self.saxpy [ number_of_blocks, threads_per_block ] (self, a, b, c)
    
    #     d_c.copy_to_host(c)
    
        # Print out the first and last 5 values of c for a quality check
        print str(c[0:5])
        print str(c[-5:])
    
t = Test()
t.main() # Execute the program