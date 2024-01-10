import numpy as np

def linear_buckets(min_freq, max_freq, num_buckets):
    bucket_size = int((max_freq - min_freq)/num_buckets)
    endpoints = []
    endpoint = min_freq
    index = 0
    while index < num_buckets:
        endpoints.append(int(endpoint))
        endpoint += bucket_size
        index += 1
    endpoints.append(max_freq)

    return endpoints


def geometric_buckets(min_freq, max_freq, num_buckets):
    endpoints = []
    index = 1
    scale = (num_buckets * (num_buckets+1))/2
    base_size = (max_freq-min_freq)/scale
    endpoints.append(min_freq)
    endpoint = min_freq
    while index < num_buckets:
        endpoint = endpoint+(base_size*index)
        endpoints.append(int(endpoint))
        index += 1
    endpoints.append(max_freq)

    return endpoints


def default_buckets():
    return [16, 38, 60, 125, 190, 250, 334, 418, 500, 1000, 1500, 2000, 2667, 3334, 4000, 5000, 6000]

"""  
Takes the result of a FFT and buckets the frequencies 
according to a provided bucket. Places the max found in amps between the bucket endpoints
into the bucket.
Helper for bucket_chunk
"""

def bucket_freqs(frequencies, buckets):
    bucketed_freqs = []
    for i in range(len(buckets)-1):
        max_amp = max(frequencies[buckets[i]:buckets[i+1]])
        bucketed_freqs.append(max_amp)
    return bucketed_freqs

"""
Takes in an amplitude array, a start index and a style of bucket to 

Input:
    - amps: Array of amplitudes, flattened, output from sf.read()
    - start: index in said Array to start the chunk of frequency analysis
    - buckets: The buckets in which we will store the frequencies
    
Output:
    - An array of maximal frequencies of each bucket
"""

def bucket_chunk(amps, start, buckets):
    max_frequency = buckets[-1]
    end = start + (max_frequency * 2)
    frequencies = abs(np.fft.fft(amps[start:end]))
    return bucket_freqs(frequencies, buckets)

"""
Scales the the result of bucket_chunk so it can be more easily visualized
"""


def scaled_frequencies(freq_bucket, max_amp, max_height):
    return max_height*(freq_bucket/max_amp)


"""
Returns the maximum value of an array of arrays
"""

def max_amps(frames):
    max_amp = 0
    for i in frames:
        if max(i) > max_amp:
            max_amp = max(i)
    return max_amp