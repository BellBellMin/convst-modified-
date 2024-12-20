# -*- coding: utf-8 -*-
"""
@author: Antoine Guillaume
"""
import numpy as np
from numpy.random import choice, uniform, random, seed
from numpy import (
    unique, where, percentile, int64, bool_, float64, concatenate,
    dot, log2, floor_divide, zeros, floor, power, ones, cumsum, mean, std,
    arange
)

from convst.transformers._commons import (
    get_subsequence, compute_shapelet_dist_vector,
    apply_one_shapelet_one_sample_multivariate, _combinations_1d,
    generate_strides_2D, prime_up_to, choice_log
)

from numba import njit, prange

from convst import (
    __USE_NUMBA_CACHE__, __USE_NUMBA_FASTMATH__,
    __USE_NUMBA_NOGIL__, __USE_NUMBA_PARALLEL__
)


@njit(cache=__USE_NUMBA_CACHE__, nogil=__USE_NUMBA_NOGIL__)
def M_SL_init_random_shapelet_params(
    n_shapelets, shapelet_sizes, n_timestamps, p_norm, max_channels, prime_scheme
):
    """
    Initialize the parameters of the shapelets.    

    Parameters
    ----------
    n_shapelets : int
        Number of shapelet to initialize
    shapelet_sizes : array, shape=()
        Set of possible length for the shapelets
    n_timestamps : int
        Number of timestamps in the input data
    p_norm : float
        A value in the range [0,1] indicating the chance for each
        shapelet to use z-normalized distance
    max_channels : int
        The maximum number of features considered for one shapelet
    prime_scheme : bool
        Wheter to only consider prime numbers as possible dilation 

        
    Returns
    -------
    values : array, shape=(n_shapelet, max(shapelet_sizes))
        An initialized (empty) value array for each shapelet
    lengths : array, shape=(n_shapelet)
        The randomly initialized length of each shapelet
    dilations : array, shape=(n_shapelet)
        The randomly initialized dilation of each shapelet
    threshold : array, shape=(n_shapelet)
        An initialized (empty) value array for each shapelet
    normalize : array, shape=(n_shapelet)
        The randomly initialized normalization indicator of each shapelet
    channels : array, shape=(n_shapelet, n_features)
        The features considered by each shapelet
    """
    # Lengths of the shapelets
    lengths = choice(shapelet_sizes, size=n_shapelets).astype(int64)

    # Dilations
    upper_bounds = log2(floor_divide(n_timestamps - 1, lengths - 1))
    if prime_scheme:
        primes = prime_up_to(int64(2**upper_bounds.max()))
        dilations = zeros(n_shapelets, dtype=int64)
        #TODO : optimize to avoid recomputing choice log for all upper bounds
        #Loop on each unique upper bounds ?
        for i in prange(n_shapelets):
            shp_primes = primes[primes<=int64(2**upper_bounds[i])]
            dilations[i] = shp_primes[choice_log(shp_primes.shape[0], 1)[0]]
    else:
        powers = zeros(n_shapelets)
        for i in prange(n_shapelets):
            powers[i] = uniform(0, upper_bounds[i])
        dilations = floor(power(2, powers)).astype(int64)
    
    # Init threshold array
    threshold = zeros(n_shapelets)

    # channels (i.e. features)
    n_channels = choice(max_channels, size=n_shapelets)+1

    channel_ids = zeros(n_channels.sum(), dtype=int64)

    # Init values array
    values = zeros(
        int64(
            dot(lengths.astype(float64), n_channels.astype(float64))
        )
    )

    # Is shapelet using z-normalization ?
    normalize = random(size=n_shapelets)
    normalize = (normalize < p_norm)

    return values, lengths, dilations, threshold, normalize, n_channels, channel_ids

@njit(cache=__USE_NUMBA_CACHE__, parallel=__USE_NUMBA_PARALLEL__, nogil=__USE_NUMBA_NOGIL__)
def M_SL_generate_shapelet(
    X, y, n_shapelets, shapelet_sizes, r_seed, p_norm, p_min, p_max, alpha,
    use_phase, max_channels, prime_scheme
):
    """
    Shapelet을 생성하고 각 shapelet이 추출된 instance와 시작 위치(start position)를 기록합니다.
    """
    n_samples, n_features, n_timestamps = X.shape
    seed(r_seed)

    # Shapelet 초기화
    values, lengths, dilations, threshold, normalize, n_channels, channel_ids = \
        M_SL_init_random_shapelet_params(
            n_shapelets, shapelet_sizes, n_timestamps, p_norm, max_channels, prime_scheme
        )

    id_samples = np.zeros(n_shapelets, dtype=np.int64)  # shapelet이 뽑힌 instance 인덱스
    start_positions = np.zeros(n_shapelets, dtype=np.int64)  # 시작 위치 기록

    unique_dil = unique(dilations)
    mask_sampling = ones((2, unique_dil.shape[0], n_samples, n_features, n_timestamps), dtype=bool_)
    mask_return = ones(n_shapelets, dtype=bool_)

    a1 = concatenate((zeros(1, dtype=int64), cumsum(n_channels * lengths)))
    a2 = concatenate((zeros(1, dtype=int64), cumsum(n_channels)))

    for i_d in prange(unique_dil.shape[0]):
        id_shps = where(dilations == unique_dil[i_d])[0]

        for i_shp in id_shps:
            _dilation = dilations[i_shp]
            _length = lengths[i_shp]
            norm = int64(normalize[i_shp])
            _n_channels = n_channels[i_shp]

            d_shape = n_timestamps if use_phase else n_timestamps - (_length - 1) * _dilation
            mask_dil = mask_sampling[norm, i_d]

            # 가능한 sampling 위치 선택
            i_mask = where(mask_dil[:, :, :d_shape].sum(axis=1) >= _n_channels * alpha)
            if i_mask[0].shape[0] > 0:
                id_sample = choice(i_mask[0])  # 선택된 instance
                id_samples[i_shp] = id_sample

                start_position = choice(i_mask[1][i_mask[0] == id_sample])  # 시작 위치 선택
                start_positions[i_shp] = start_position  # 시작 위치 기록

                _values = zeros(_n_channels * _length)
                _channel_ids = choice(arange(0, n_features), _n_channels, replace=False)
                a3 = 0

                for k in range(_n_channels):
                    b3 = a3 + _length
                    _v = get_subsequence(
                        X[id_sample, _channel_ids[k]], start_position, _length, _dilation, norm, use_phase
                    )
                    _values[a3:b3] = _v
                    a3 = b3

                values[a1[i_shp]:a1[i_shp+1]] = _values
                channel_ids[a2[i_shp]:a2[i_shp+1]] = _channel_ids

    return (
        values, lengths, dilations, threshold, normalize, n_channels, channel_ids
    ), id_samples, start_positions
    

@njit(cache=__USE_NUMBA_CACHE__, parallel=__USE_NUMBA_PARALLEL__, fastmath=__USE_NUMBA_FASTMATH__, nogil=__USE_NUMBA_NOGIL__)
def M_SL_apply_all_shapelets(
    X, shapelets, use_phase
):
    """
    Apply a set of generated shapelet using the parameter arrays previously 
    generated to a set of time series.

    Parameters
    ----------
    X : array, shape=(n_samples, n_features, n_timestamps)
        Input time series
    shapelets: set of array, shape=(5)
        values : array, shape=(n_shapelets, max(shapelet_sizes))
            Values of the shapelets. If the shapelet use z-normalized distance,
            those values are already z-normalized by the shapelet 
            initialization step.
        lengths : array, shape=(n_shapelets)
            Length parameter of the shapelets
        dilations : array, shape=(n_shapelets)
            Dilation parameter of the shapelets
        threshold : array, shape=(n_shapelets)
            Threshold parameter of the shapelets
        normalize : array, shape=(n_shapelets)
            Normalization indicator of the shapelets
    use_phase: bool
        Wheter to use phase invariance
    
    Returns
    -------
    X_new : array, shape=(n_samples, 3*n_shapelets)
        The transformed input time series with each shapelet extracting 3
        feature from the distance vector computed on each time series.

    """
    (values, lengths, dilations, threshold, 
     normalize, n_channels, channel_ids) = shapelets
    n_shapelets = len(lengths)
    n_samples, n_ft, n_timestamps = X.shape
    n_features = 3
    
    #(u_l * u_d , 2)
    params_shp = _combinations_1d(lengths, dilations)
    #(u_l * u_d) + 1
    n_shp_params = zeros(params_shp.shape[0]+1, dtype=int64)
    #(n_shapelets)
    idx_shp = zeros(n_shapelets, dtype=int64)
    
    #Indexes per shapelets for values array
    a1 = concatenate((zeros(1, dtype=int64),cumsum(n_channels*lengths)))
    #Indexes per shapelets for channel_ids array
    a2 = concatenate((zeros(1, dtype=int64),cumsum(n_channels)))
    # Counter for shapelet params array
    a3 = 0
    
    for i in range(params_shp.shape[0]):
        _length = params_shp[i, 0]
        _dilation = params_shp[i, 1]
        
        ix_shapelets = where((lengths == _length) & (dilations == _dilation))[0]
        b = a3 + ix_shapelets.shape[0]
        
        idx_shp[a3:b] = ix_shapelets
        n_shp_params[i+1] = ix_shapelets.shape[0]
        
        a3 = b
    n_shp_params = cumsum(n_shp_params)
    
    X_new = zeros((n_samples, n_features * n_shapelets))
    for i_sample in prange(n_samples):
        #n_shp_params is a cumsum starting at 0
        for i_shp_param in prange(n_shp_params.shape[0]-1):
            _length = params_shp[i_shp_param, 0]
            _dilation = params_shp[i_shp_param, 1]
            
            strides = generate_strides_2D(
                X[i_sample], _length, _dilation, use_phase
            )
            # Indexes of shapelets corresponding to the params of i_shp_param
            _idx_shp = idx_shp[n_shp_params[i_shp_param]:n_shp_params[i_shp_param+1]]
            
            _idx_no_norm = _idx_shp[where(normalize[_idx_shp] == False)[0]]
            for i_idx in range(_idx_no_norm.shape[0]):               
                i_shp = _idx_no_norm[i_idx]
                _channels = channel_ids[a2[i_shp]:a2[i_shp+1]]
                _values = values[a1[i_shp]:a1[i_shp+1]].reshape(
                    n_channels[i_shp], _length
                )

                X_new[i_sample, (n_features * i_shp):(n_features * i_shp + n_features)] = \
                apply_one_shapelet_one_sample_multivariate(
                    strides[_channels], _values, threshold[i_shp]
                )
                        
            _idx_norm = _idx_shp[where(normalize[_idx_shp] == True)[0]]
            if _idx_norm.shape[0] > 0:
                #n_features
                for i_stride in range(strides.shape[0]):
                    #n_timestamps
                    for j_stride in range(strides.shape[1]):
                      _str = strides[i_stride,j_stride]
                      strides[i_stride,j_stride] = (_str - mean(_str))/(std(_str)+1e-8)
                          
                for i_idx in range(_idx_norm.shape[0]):               
                    i_shp = _idx_norm[i_idx]
                    _channels = channel_ids[a2[i_shp]:a2[i_shp+1]]
                    _values = values[a1[i_shp]:a1[i_shp+1]].reshape(
                        n_channels[i_shp], _length
                    )
                    
                    X_new[i_sample, (n_features * i_shp):(n_features * i_shp + n_features)] = \
                    apply_one_shapelet_one_sample_multivariate(
                        strides[_channels], _values, threshold[i_shp]
                    )
    return X_new