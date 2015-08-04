#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylab import *
from modshogun import *
import numpy, matplotlib.pyplot, random, pdb
from tools.load import LoadMatrix

# Loading toy data from files
def load_Toy(dataRoute, fileTrain, fileLabels):
	lm = LoadMatrix()
	dataSet = lm.load_numbers(dataRoute + fileTrain)
	labels = lm.load_labels(dataRoute + fileLabels)

	return (dataSet.T[0:3*len(dataSet.T)/4].T, 	# Return the training set, 3/4 * dataSet
		    dataSet.T[(3*len(dataSet.T)/4):].T,	# Return the test set, 1/4 * dataSet
	        labels[0:3*len(labels)/4], 		    # Return corresponding train and test labels
		    labels[(3*len(labels)/4):])

# 2D Toy data generator
def generate_binToy():
	num=30;
	num_components=4
	means=zeros((num_components, 2))
	means[0]=[-1,1]
	means[1]=[2,-1.5]
	means[2]=[-1,-3]
	means[3]=[2,1]

	covs=array([[1.0,0.0],[0.0,1.0]])

	gmm=GMM(num_components)
	[gmm.set_nth_mean(means[i], i) for i in range(num_components)]
	[gmm.set_nth_cov(covs,i) for i in range(num_components)]
	gmm.set_coef(array([1.0,0.0,0.0,0.0]))
	xntr=array([gmm.sample() for i in xrange(num)]).T
	xnte=array([gmm.sample() for i in xrange(5000)]).T
	gmm.set_coef(array([0.0,1.0,0.0,0.0]))
	xntr1=array([gmm.sample() for i in xrange(num)]).T
	xnte1=array([gmm.sample() for i in xrange(5000)]).T
	gmm.set_coef(array([0.0,0.0,1.0,0.0]))
	xptr=array([gmm.sample() for i in xrange(num)]).T
	xpte=array([gmm.sample() for i in xrange(5000)]).T
	gmm.set_coef(array([0.0,0.0,0.0,1.0]))
	xptr1=array([gmm.sample() for i in xrange(num)]).T
	xpte1=array([gmm.sample() for i in xrange(5000)]).T

	return (concatenate((xntr,xntr1,xptr,xptr1), axis=1), 	#Train Data
		 	concatenate((xnte,xnte1,xpte,xpte1), axis=1), 	#Test Data
		 	concatenate((-ones(2*num), ones(2*num))),	    #Train Labels
		 	concatenate((-ones(10000), ones(10000))) )	    #Test Labels
	

def sigmaGen(self, hyperDistribution, size, rango, parameters):
    """
     Creating guassian kernels
     This module generates the pseudorandom vector of witdts for basis Gaussian kernels
     according to a distribution, i.e.:
     hyperDistribution = 
                         ['linear'| 
                          'quadratic'|
                          'log-gauss'|
                          'gaussian'|
                          'triangular'|
                          'pareto'|
                          'beta'|
                          'gamma'|
                          'weibull']. 
    See http://pymotw.com/2/random/ for details about pseudorandom number
    generators in python.
    The input 'size' is the amount of segments the distribution domain will 
    be discretized out. The 'rango' input are the minimum and maximum
    values of the obtained distributed values. The 'parameters' of these 
    weight vector distributions are set to common values of each distribution
    by default, but they can be modified.
    """
#	_l = 10		
#	sig = linspace(0.01, _l, size)[::-1]
    sig = []        
    if hyperDistribution == 'linear':
        #for i in xrange(size):
        sig = random.sample(range(rango[0], rango[1]),size)
        return sig
    elif hyperDistribution == 'quadratic':
        #for i in xrange(size):
        #pdb.set_trace()
        sig = random.sample(range(rango[0],int(sqrt(rango[1]))), size)
        return numpy.array(sig)**2
    elif hyperDistribution == 'gaussian':
        i = 0
        while i < size:
            numero = random.gauss(parameters[0], parameters[1])
            if numero > rango[0] and numero < rango [1]:  # Validate the initial point of
                sig.append(numero)
                i += 1                      # 'range'. If not met, loop does
        #pdb.set_trace()                                    # not end, but resets.
                                            # If met, the number is appended 
        return sig                 # to 'sig' width list.
    elif hyperDistribution == 'triangular':
        for i in xrange(size):
            sig.append(random.triangular(rango[0], rango[1]))
        return sig
    elif hyperDistribution == 'beta':
        i = 0
        while i < size:
            numero = random.betavariate(parameters[0], parameters[1]) * (rango[1] - rango[0]) + rango[0]
            #if numero > rango[0] and numero < rango [1]:# Validate the initial point of
            sig.append(numero)
            i += 1         # If met, the number is appended 
        return sig                 # to 'sig' width list.
    elif hyperDistribution == 'pareto':
        return numpy.random.pareto(5, size = size) * (rango[1] - rango[0]) + rango[0]                          # to 'sig' width list.	 
    elif hyperDistribution == 'gamma':
        return numpy.random.gamma(shape = 1, size = size) * (rango[1] - rango[0]) + rango[0]
                         		    
    elif hyperDistribution == 'weibull':
         return numpy.random.weibull(2, size = size) * (rango[1] - rango[0]) + rango[0]   	    
 
    elif hyperDistribution == 'log-gauss':
        i = 0
        while i < size:
            numero = random.lognormvariate(parameters[0], parameters[1])
            if numero > rango[0] and numero < rango [1]:# Validate the initial point of
                sig.append(numero)
                i += 1                      # 'range'. If not met, loop does

        return sig   	    	    
    else:
    	print 'The entered hyperparameter distribution is not allowed.'
# -------------------------------------------------------------------
# combine kernels
def genKer(self, featsL, featsR, basisFam, widths = [5,4,3,2,1]):
    '''This module generates a list of Gaussian Kernels. These kernels are 
    tuned according to the vector ''widths''. Input parameters ''featsL''
    and ''featsR'' are Shogun feature objects. In the case of a learnt RKHS
    these both objects should be derived from the training SLM vectors, 
    through the Shogun constructor realFeatures().
    This module also appends kernels to a combinedKernel object. The kernels
    to be append are ''kernels'' and then are append to the linear combination 
    'combKer', which is returned. We have analyzed some basis families available
    in Shogun, so possible values of 'basisFam':
    basisFam = ['gaussian', 
                'inverseQuadratic', 
                'polynomial', 
                'power', 
                'rationalQuadratic', 
                'spherical', 
                'tstudent', 
                'wave', 
                'wavelet', 
                'cauchy', 
                'exponential']
    '''
    print 'Widths:'
    kernels = []
    if basisFam == 'gaussian':
        for w in widths:
            kernels.append(GaussianKernel())#l = featsL, r = featsR))
            kernels[len(kernels)-1].set_width(w)
            if self._verbose:    
                print kernels[len(kernels)-1].get_width()
    elif basisFam == 'inverseQuadratic': # For this (and others below) kernel it is necessary fitting the 
        dst = MinkowskiMetric (l = featsL, r = featsR, k = 2) # distance matrix at this moment
        for w in widths:
            kernels.append(InverseMultiQuadricKernel(0, w, dst)) 
        if self._verbose:    
            print widths
    elif basisFam == 'polynomial':      
        for w in widths:
            kernels.append(PolyKernel(0, w, False)) 
        if self._verbose:    
            print widths
    elif basisFam == 'power': # At least for images, the used norm does not make differences in performace
        dst = MinkowskiMetric (l = featsL, r = featsR, k = 2)     
        for w in widths:
            kernels.append(PowerKernel(0, w, dst)) 
        if self._verbose:    
            print widths  
    elif basisFam == 'rationalQuadratic': # At least for images, using 3-norm  make differences 
        dst = MinkowskiMetric (l = featsL, r = featsR, k = 2) # in performace    
        for w in widths:
            kernels.append(RationalQuadraticKernel(0, w, dst)) 
        if self._verbose:    
            print widths  
    elif basisFam == 'spherical': # At least for images, the used norm does not make differences in performace
        dst = MinkowskiMetric (l = featsL, r = featsR, k = 2) 
        for w in widths:
            kernels.append(SphericalKernel(0, w, dst)) 
        if self._verbose:    
            print widths  
    elif basisFam == 'tstudent': # At least for images, the used norm does not make differences in performace
        dst = MinkowskiMetric (l = featsL, r = featsR, k = 2) 
        for w in widths:
            kernels.append(TStudentKernel(0, w, dst)) 
        if self._verbose:    
            print widths 
    elif basisFam == 'wave': # At least for images, the used norm does not make differences in performace
        dst = MinkowskiMetric (l = featsL, r = featsR, k = 2) 
        for w in widths:
            kernels.append(WaveKernel(0, w, dst)) 
        if self._verbose:    
            print widths    
    elif basisFam == 'wavelet': # At least for images it is very low the performance with this kernel.
        for w in widths:        # It remains pending, for now, analysing its parameters.
            kernels.append(WaveletKernel(0, w, 0)) 
        if self._verbose:    
            print widths   
    elif basisFam == 'cauchy': 
        dst = MinkowskiMetric (l = featsL, r = featsR, k = 2)
        for w in widths:
            kernels.append(CauchyKernel(0, w, dst))            
        if self._verbose:    
            print widths
    elif basisFam == 'exponential': # For this kernel it is necessary specifying features at the constructor
        dst = MinkowskiMetric (l = featsL, r = featsR, k = 2)
        for w in widths:
            kernels.append(ExponentialKernel(featsL, featsR, w, dst, 0))            
        if self._verbose:    
            print widths
    elif basisFam == 'anova': # This kernel presents a warning in training: 
        """RuntimeWarning: [WARN] In file /home/iarroyof/shogun/src/shogun/classifier/mkl/MKLMulticlass.cpp line
           198: CMKLMulticlass::evaluatefinishcriterion(...): deltanew<=0.Switching back to weight norsm
           difference as criterion.
        """   
        for w in widths:
            kernels.append(ANOVAKernel(0, w)) 
        if self._verbose:    
            print widths
    else:
        raise NameError('Unknown Kernel family name!!!')       
        
    combKer = CombinedKernel()
    for k in kernels:
        combKer.append_kernel(k)   

    return combKer

# Defining the compound kernel object
class mklObj:
    """Default automated definition of the mutiple kernel learning object."""
    def __init__(self, weightRegNorm = 2, regPar = 2, epsilon = 1e-5, 
	 			 threads = 2, mkl_epsilon = 0.001, binary = False, verbose = False):
	 	
        if binary:
            self.mkl = MKLClassification()	# MKL object (Multiclass)
            self.mkl.set_C(regPar, 1)		# Setting binary regularization parameter and regularization norm	
        else:		 
            self.mkl = MKLMulticlass()		# MKL object (Binary)
            self.mkl.set_C(regPar)		# Setting multiclass regularization  parameter

        self.mkl.set_mkl_norm(weightRegNorm)		# Setting the weight vector norm
        self.mkl.set_epsilon(epsilon) 			# setting the transducer epsilon
        self.mkl.set_mkl_epsilon(mkl_epsilon)		# setting the MKL stop criterion. The value suggested by Shogun is 0.001
        self.mkl.parallel.set_num_threads(threads) 	# setting number of traing threads
        self._verbose = verbose				# inner trainig process verbosing flag
        self._binary = binary
# All obtained objects below become class attributes, so they are available any moment.
# Self Function for kernel generation

    def fit_kernel(self, featsTr,  targetsTr, featsTs, targetsTs, 
                   randomRange = [1, 50], randomParams = [1, 1], 
	               hyper = 'linear', kernelFamily = 'guassian', pKers = 3):
	    # Generating the widths:
        # sigmaGen(self, hyperDistribution, size, rango = [1,50], parameters = [0, 0])
        #if kernelFamily == 'gaussian' or kernelFamily == 'chi2':
        self.sigmas = sorted(sigmaGen(self, hyperDistribution = hyper, size = pKers, 
		                       rango = randomRange, parameters = randomParams)) #; pdb.set_trace()
        try: # Verifying if number of kernels is greater or equal to 2
            if pKers <= 1 or len(self.sigmas)<2:
                raise NameError('Senseless MKLClassification use!!!')
        except NameError:	    	
            print "-----------------------------------------------------"
            print """The multikernel learning object is meaningless for less than 2 basis 
				 kernels, i.e. pKers <= 1, so 'mklObj' couldn't be instantiated."""
            print "-----------------------------------------------------"
            raise
        self._featsTr = featsTr 		# Inner variable copying.
        self._targetsTr = targetsTr		
        self._hyper = hyper
        self._pkers = pKers
        if self._verbose:	# Printing the training progress
            print '\nNacho, multiple <' + kernelFamily + '> Kernels have been initialized...'
            print "\nInput main parameters: "
            print "Hyperarameter distribution: ", self._hyper, "\nLinear combination size: ", pKers
            if not self._binary: 
                print "Classes: ", targetsTr.get_num_classes()
            else:
                print "Classes: Binary" 
		
# Generating the list of subkernels. Creating the compound kernel
# For monomial-nonhomogeneous polynomial kernels the hyperparameters are uniquely the degree of each monomial
# in the form of a sequence. MKL finds the coefficient for each monomial in order to find a polynomial.
        if kernelFamily == 'polynomial' or kernelFamily == 'power' or kernelFamily == 'tstudent' or kernelFamily ==  'anova':
            self.ker = genKer(self, self._featsTr, self._featsTr, basisFam = kernelFamily, widths = list(range(0,pKers)))
        else:
            self.ker = genKer(self, self._featsTr, self._featsTr, basisFam = kernelFamily, widths = self.sigmas)
# Initializing the compound kernel
        self.ker.init(self._featsTr, self._featsTr)
        try: # Verifying if number of kernels is greater or equal to 2
            #if not inn: 
            #    raise NameError('Multikernel wasn\'t initialized!!!')
            if self.ker.get_num_subkernels() < 2:
                raise NameError('Multikernel coeffients are less than 2!!!')
        except NameError:	    	
            raise
        
# Verbose for learning surveying	
        if self._verbose:
            print '\nKernel fitted...'
# Initializing the transducer for multiclassification
        self.mkl.set_kernel(self.ker)
        self.mkl.set_labels(self._targetsTr)# ; pdb.set_trace()
# Train to return the learnt kernel
        if self._verbose:
            print '\nLearning the machine coefficients...'
        self.mkl.train() 
        #pdb.set_trace()
        if self._verbose:		
            print 'Kernel trained... Weights: ', self.ker.get_subkernel_weights()
# Evaluate the learnt Kernel. Here it is asumed 'ker' is learnt, so we only
# need for initialize it again but with the test set object. Then, set the
# the initialized kernel to the mkl object in order to 'apply'.
        self.ker.init(self._featsTr, featsTs)	# Now with test examples. The inner product between training
        self.mkl.set_kernel(self.ker)		    # and test examples generates the corresponding Gramm Matrix.
        out = self.mkl.apply()			        # Applying the obtained Gramm Matrix

        if self._binary:			    # If the problem is either binary or multiclass, different 
            evalua = ErrorRateMeasure()	# performance measures are computed.
        else:    
            evalua = MulticlassAccuracy()
        self.testerr = evalua.evaluate(out, targetsTs)
# Verbose for surveying		
        if self._verbose:
            if self._binary:
                print 'Kernel evaluation ready. The precision was: ', 100-self.testerr*100, '%'		
            else:
                print 'Kernel evaluation ready. The precision was: ', self.testerr*100, '%'
# Save sigmas into a file if required. By default, '../sigmasFile.txt' will be the corresponding directory and  
# file name. You can change the mode of the file object, e.g. to 'a' for uniquely adding content. If you want  
# adding some note for identifying each sigma array, it could be used the 'note' input string.
    def save_sigmas(self, file = '../sigmasFile.txt', mode = 'w', note = 'Some note'):
        f = open(file, mode)
        f.write('------------------------ '+ note +' ----------------------')
        for s in self.sigmas:		
            f.write("%s, " % s)
        f.close()

# Multikernel object training procedure file reporting.
    def filePrintingResults (self, fileName, mode):
		f = open(fileName, mode)
		if mode == 'w':
		    f.write('                   Results\
		    \n--------------------------------------------------------------------\n')
		else:
		    f.write('\n--------------------------------------------------------------------\n')
		f.write("Linear combination size: " + str(self._pkers)) 
	  	f.write('\nHyperarameter distribution: ' + str(self._hyper) )		
	  	f.write("\nWeights: ") 
	  	ws = self.ker.get_subkernel_weights()
		for item in ws:
			f.write("%s, " % item)
		f.write('\nWidths: ') 
		for item in self.sigmas:
			f.write("%s, " % item)
		if self._binary:
	  		f.write('\nTest error: ' + str(100 - self.testerr*100) )
	  	else:
	  		f.write("\nClasses: " + str(self._targetsTr.get_num_classes()) )
	  		f.write('\nTest error:' + str( self.testerr*100 ))			
		f.close()

# It is pending defining functions for run time attribute modification, e.g. set_verbose(), 
# set_regPar(), etc.

# Return kernel 'ker' as well as other useful values obtained during the training:		
    def get_combKernel (self): return self.ker
    def get_testErr (self): return self.testerr
    def get_weights (self): return self.ker.get_subkernel_weights()
    def get_sigmas (self): return self.sigmas
	
# ------------------------------ MAIN ----------------------------------------------------------------------
# MKL object Default definition:
# class mklObj:
#   def __init__(self, weightRegNorm = 2, regPar = 2, epsilon = 1e-5, 
#	 			 threads = 2, mkl_epsilon = 0.001, binary = False, verbose = False):
#
# Kernel fitting function
# fit_kernel(self, featsTr,  targetsTr, featsTs, targetsTs, 
#                randomRange = [1, 50], randomParams = [1, 1], 
#	             hyper = 'linear', kernelFamily = 'guassian', pKers = 3):
# ----------------------------------------------------------------------------------------------------------
#### Loading train and test data
# 1) For multiclass problem loaded from file:
[traindata, 
 testdata, 
 trainlab, 
 testlab] = load_Toy('/home/iarroyof/shogun-data/toy/',         # Data directory
                     'fm_train_multiclass_digits500.dat',       # Multiclass dataSet examples file name
                     'label_train_multiclass_digits500.dat')    # Multiclass Labels file name
# 2) For generated binary problem:
#[traindata, testdata, trainlab, testlab] = generate_binToy()

#### Casting train and test data for Shogun feature objects (uncomment and comment labels according to your problem)
feats_train = RealFeatures(traindata) 	# train examples
#labelsTr = BinaryLabels(trainlab)	    # train binary lables   
labelsTr = MulticlassLabels(trainlab)	# train multiclass labels
feats_test = RealFeatures(testdata)  	# test examples
#labelsTs = BinaryLabels(testlab)	    # test binary labels
labelsTs = MulticlassLabels(testlab)	# test multiclass labels

#### Instantiating the learnable kernel object
kernelO = mklObj(verbose = True, threads = 4)
# It is possible resetting the kernel for different principal parameters.
# *** It is pending programming a method for loading from file a list of
# principal parameters.***
#### With m basis kernels:
basisKernelFamily = ['gaussian', 
                    'inverseQuadratic', 
                    'polynomial', 
                    'power', 
                    'rationalQuadratic', 
                    'spherical', 
                    'tstudent', 
                    'wave', 
                    'wavelet', 
                    'cauchy', 
                    'exponential']

#### With different kernel parameter distributions:               
widthDistribution = ['linear',
                    'quadratic',
                    'log-gauss',
                    'gaussian',
                    'triangular',
                    'pareto',
                    'beta',
                    'gamma',
                    'weibull']
           
mode = 'w'
"""for w in widthDistribution:
    kernelO.fit_kernel(featsTr = feats_train, 
				   targetsTr = labelsTr, 
				   featsTs = feats_test, 
				   targetsTs = labelsTs, 
				   randomRange = [1, 200], 
				   randomParams = [50, 20], # for quadratic there are not parameter distribution
				   hyper = w, 
				   pKers = 10)
    kernelO.filePrintingResults('mkl_output.txt', mode)	# Printing to a file the training file report.
    mode = 'a'
"""
#### With n basis kernels
# Falta hacer funciones para habilitar la opción de cargar sigmas desde archivo.
kernelO.fit_kernel(featsTr = feats_train, 
				   targetsTr = labelsTr, 
				   featsTs = feats_test, 
				   targetsTs = labelsTs, 
				   kernelFamily = 'poly',
				   randomRange = [50, 200], # For homogeneous polynomial kernels these two parameter sets 
				   randomParams = [50, 20], # have not effect. For quadratic there are not parameter distribution
				   hyper = 'linear', 
				   pKers = 2)
