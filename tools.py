from math import ceil
from time import time

import h5py
import numpy as np

KMER_CODES = {ord('A'): '00', ord('C'): '01', ord('G'): '10', ord('T'): '11'}

def timer(func):
    def wrapper(*args, **kwargs):
        t_init = time()
        res = func(*args, **kwargs)
        duration = time() - t_init

        print("{}: {} s".format(func.__name__, duration))
        return res

    return wrapper

def get_kmer_number(sequence, k=4):
    kmer_encoding = sequence.translate(KMER_CODES)
    kmer_indices = [int(kmer_encoding[i:i+2*k], 2) for i in range(0, 2*(len(sequence)-k+1), 2)]

    return kmer_indices

def get_kmer_frequency(sequence, kmer_list=[4], rc=False, index=False, norm=False):

    output_sizes = np.cumsum([0]+[int(4**k/(1+rc)) for k in kmer_list])
    frequencies = np.zeros(output_sizes[-1])

    for i, k in enumerate(kmer_list):

        if not index:
            kmer_indices = get_kmer_number(sequence, k)
        else:
            kmer_indices = sequence

        freq_k = np.bincount(kmer_indices, minlength=4**k)
        if rc:
            freq_k += freq_k[::-1]
            freq_k = freq_k[:int(4**k/2)]

        if norm:
            freq_k = freq_k / np.sum(freq_k)

        frequencies[output_sizes[i]:output_sizes[i+1]] = freq_k

    return frequencies

def get_coverage(pairs, coverage_h5, window_size, window_step):
    h5data = h5py.File(coverage_h5)
    contigs = np.unique(pairs['sp'].flatten())

    coverage_data = {ctg: np.array(h5data.get(ctg)[:]) for ctg in contigs}

    n_pairs = len(pairs)
    n_samples, _ = np.array(list(coverage_data.values())[0]).shape
    frag_len = pairs['end'][0, 0] - pairs['start'][0, 0]

    pairs = np.concatenate([pairs[:, 0], pairs[:, 1]])
    sorted_idx = np.argsort(pairs['sp'])

    conv_shape = ceil((frag_len-window_size+1)/window_step)

    coverage_feature = np.zeros([2*n_pairs, n_samples, conv_shape],
                                dtype=np.float32)
    seen = {}

    for i, (species, start, end) in enumerate(pairs[sorted_idx]):
        cov_sp = seen.get((species, start), None)

        if i%100 == 0:
            print("{:,}/{:,}".format(i, pairs.shape[0]), end='\r')

        if cov_sp is None:
            cov_sp = np.apply_along_axis(
                lambda x: avg_window(x, window_size, window_step),
                1,
                coverage_data[species][:, start:end]
            )
            seen[(species, start)] = cov_sp

        coverage_feature[sorted_idx[i]] = cov_sp

    return (coverage_feature[:n_pairs, :, :],
            coverage_feature[n_pairs:, :, :])

def avg_window(x, window_size, window_step):
    x_conv = np.convolve(x, np.ones(window_size)/window_size, mode="valid")
    return x_conv[::window_step]
