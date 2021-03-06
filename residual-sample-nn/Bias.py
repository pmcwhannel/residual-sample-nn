# Standard imports.
import numpy as np

# Class bias.
class Bias():

    def __init__(self, n_nodes, distribution='gaussian'):
        '''
        Creates class Bias and saves it in variable "bias_vector" in class Layer.

        @param n_nodes: The number of nodes in the hidden layer
        @param distribution: The distribution class Bias follows. Default is Gaussian.
        @returns: None.
        '''
        self.n = abs(int(n_nodes))    # Number of nodes in the hidden layer
        self.dis = str(distribution) # Distribution type
        # When distribution is gaussian
        if self.dis == 'gaussian':
            self.mu = np.zeros((1, self.n))
            self.sigma = np.zeros((1, self.n))

    def Initialize_Bootstrap(self, times):
        '''
        Initialize the 3D matrix within the class we sample from.

        @param times: The number of times we sample the bias.
        @returns: None.
        '''
        # Ensures datatype.
        times = abs(int(times))
        self.bootstrap_matrix= []  # Initialze the matrix.
        if self.dis == 'gaussian':
            for _ in range(times):
                # Sample from the distribution and append to the matrix.
                bias = np.random.normal(self.mu, self.sigma, size=[1,self.n])
                self.bootstrap_matrix.append(bias)

    def Sample(self, bootstrap):
        '''
        Sample the data from the distribution class Bias follows.
        
        @param bootstrap: Boolean. If true, using bootstrap to sample.
            Otherwise, sample using distribution parameters.
        @returns: (bias), the bias vector used in Feedforward.
        '''
        bootstrap = bool(bootstrap)
        if self.dis == 'gaussian':
            # When bootstrap == False, sample from distribution directly.
            if not bootstrap:
                bias = np.random.normal(self.mu, self.sigma, size=[1,self.n])
            else:
                # Otherwise using bootstrap.
                max_len = len(self.bootstrap_matrix)
                idx_vector = np.random.randint(max_len, size = (1, self.n))
                bias = self.idx2element(idx_vector, self.bootstrap_matrix)
        return bias


    def idx2element(self, index_vector, data):
        '''
        Using index matrix to get element matrix with same dimension.

        @param index_vector: Vector of size (1 x self.n). Elements are randomly selected indices.
        @param data: Matrix of size (times x 1 x self.n). Each element is "bias" sampled from distribution.
        @returns: (bootstrap_data), element vector corresponding to index_vector from data.
        '''
        bootstrap_data = np.zeros((1, self.n))  # Same size.
        for i in range(len(index_vector)):
            for j in range(len(index_vector[0])):
            # Using the index to select element.
                bootstrap_data[i][j] = data[index_vector[i][j]][i][j]
        return bootstrap_data


    def Update(self, lst, times, bootstrap, coefficient):
        '''
        Update distribution parameters using many samples.
        
        @param lst: A list of samples we use to update.
        @param times: Number of times we sampled. 
            It's also the number of elements in lst.
        @param bootstrap: Boolean, Whether or not to bootstrap.
        @param coefficient: Sigma = coefficient * mean.
            Note: Usually we use sample variance to update sigma. 
            However, it converges to zero. Therefore we use coefficient.
        @returns: None.
        '''
        self.bootstrap_matrix = lst # Update bootstrap_matrix.
        times = abs(int(times))
        coefficient = abs(float(coefficient))
        bootstrap = bool(bootstrap)
        if bootstrap:
            # Update mu using sample mean.
            self.mu = np.sum(lst, 0) / times
        # When normal, the distribution parameters are mu and sigma.
        elif self.dis == 'gaussian':
            # Update mu using sample mean.
            self.mu = np.sum(lst, 0) / times
            # Update sigma using coefficient * self.mu, need to be non-negative.
            self.sigma = abs(self.mu) * coefficient
