This folder contains transformers for convolutional kernels and convolutional shapelets. Note that most are not used in the algorithm itself to avoid manipulating objects, which do not fit in the numba paradigm and are not quite as efficient time or memory wise.
Instead they are mostly used in the examples section for clarity to avoid using complex array structures when presenting the algorithm.