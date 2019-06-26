dataset = "sim"

io_path = {
    'in': "input_data/{}".format(dataset),
    'out': "output_data/{}".format(dataset)
}

frag_len = 1024
min_genome_length = 2*frag_len
step = int(frag_len/8)
n_frags = 50
kmer = 4
add_rc = False

train_args = {
    'batch_size': 64,
    'learning_rate': 1e-4,
    'window_size': 16,
    'load_batch': 2000,
    'kmer': kmer
}

nn_arch = {
    'composition': { 'neurons': [128,64] },
    'coverage': { 'neurons': [128,64],
                  'n_filters': 64, 'kernel_size': 16,'conv_stride': 8,
                  'pool_size': 4, 'pool_stride': 2},
    'combination': { 'neurons': [32] }
}
