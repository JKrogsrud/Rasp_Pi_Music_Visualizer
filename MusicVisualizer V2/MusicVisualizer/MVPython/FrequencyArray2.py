import numpy as np


""" 
frame_rate is the number of amplitudes sampled per second in the sound file
amplitudes is the (2,N) or (1,N) array of amplitudes
both of these are the output of using scipy.io.wavfile's read method
frames_per_second is the users desired frames_per_second in the final visualization

This function returns a 16 by (Amplitudes.size / frames_per_second) Array
"""

def freq_array(frame_rate, amplitudes, frames_per_second):

    # Some files have 2 channels of amplitudes, in this case let's just add the channels together
    if len(np.shape(amplitudes)) > 1:
        amplitudes = amplitudes[:, 0] + amplitudes[:, 1]

    # Here we create a new array in which every entry in this new array will be an array of the frequencies
    # that appear in a specified chunk of time.

    freq_over_time = []
    frame_jump = int(frame_rate/frames_per_second)  # How much we increase our time_marker by for the next sample
    time_marker = 0                                 # Starting index
    #max_amp = 0                                     # largest amplitude found so far for scaling purposes
    max_amps = []                              # keep track of the max amps found for scaling

    # We make sure we don't sample past the amplitudes
    amplitudes = amplitudes[::2] # Cut out every 4th element
    frame_rate = int(frame_rate/2)
    while time_marker + frame_rate < len(amplitudes):
        batch_frequencies = abs(np.fft.fft(amplitudes[time_marker:time_marker+frame_rate]))  # The Magic really happens here
        freq_over_time.append(batch_frequencies)
        
        max_amps.append(max(batch_frequencies))
        
        #if np.percentile(batch_frequencies, 99) > max_amp:  # Update our max_amp, choosing the 60th percentile here
            #max_amp = np.percentile(batch_frequencies, 99) 

        time_marker += frame_jump  # Move to next batch of frames to sample
    
    max_amp = np.percentile(max_amps, 75)
    
    # We now have a list of arrays at different times, we just need to clean it up a bit for the visualizer
    # We will go through each frame and instead of taking all the frequencies we will look only at the maximum over
    # various subintervals representing 2 in sub-bass, 3 each in bass, lower midrange, midrange, higher midrange
    # and 2 in presence.
    # Afterwards we scale everything by dividing the list by the max_freq and multiplying by 32 so we range
    # between 0 and 32.

    freq_bins = np.empty(shape=(1, 16))
    for freq_batch in freq_over_time:
        fbin = np.empty(1,)
        fbin = np.append(fbin, max(freq_batch[4:20]))      # sub-bass
        fbin = np.append(fbin, max(freq_batch[21:30]))
        fbin = np.append(fbin, max(freq_batch[31:50]))     # bass
        fbin = np.append(fbin, max(freq_batch[51:70]))
        fbin = np.append(fbin, max(freq_batch[71:90]))
        fbin = np.append(fbin, max(freq_batch[91:110]))
        fbin = np.append(fbin, max(freq_batch[111:125]))
        fbin = np.append(fbin, max(freq_batch[126:145]))    # Lower Midrange
        fbin = np.append(fbin, max(freq_batch[146:185]))
        fbin = np.append(fbin, max(freq_batch[186:215]))
        fbin = np.append(fbin, max(freq_batch[216:250]))
        fbin = np.append(fbin, max(freq_batch[251:624]))   # Midrange
        fbin = np.append(fbin, max(freq_batch[625:1000]))
        fbin = np.append(fbin, max(freq_batch[1001:1500]))  # Higher Midrange
        fbin = np.append(fbin, max(freq_batch[1501:2000]))
        fbin = np.append(fbin, max(freq_batch[2001:3000]))  # Presence
        fbin = 32 * (fbin / max_amp)
        freq_bins = np.append(freq_bins, [fbin[1:]], axis=0)

    # Done! We can return the new array for processing into bars

    return freq_bins

