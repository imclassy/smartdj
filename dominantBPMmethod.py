import librosa, librosa.display
import math
import numpy
import operator
from mutagen.mp3 import MP3

_SEGMENTS_LENGTH_IN_SECONDS = 4
_BPM_ACCEPTED_MARGIN_IN_SECONDS = 3
#songs = ['flames.mp3', 'no_es_justo.mp3', 'i_like_it_like_that.mp3', 'mocca.mp3', 'borracha.mp3', 'peligrosa.mp3', 'ambiente.mp3' ]
songs = ['i_like_it_like_that.mp3', 'mocca.mp3']
#songs = ['flames.mp3']

#Returns the time stamp of the current song and the next song where there should be a transition
def getTransitionTimes(time_stamp_a, intervalsBPMS_a, grouped_beats_a, intervalsBPMS_b, grouped_beats_b):
    beat_time_stamp_b = 0
    beat_time_stamp_a = 0
    interval_a = None
    interval_b = None
    bpm_a = 0
    beats_a = []

    #find the interval and the bpm of the current song time stamp
    for interval in intervalsBPMS_a.keys():
        start, end = interval
        if (time_stamp_a >= start) and (time_stamp_a < end):
            bpm_a = intervalsBPMS_a[interval]
            interval_a = interval
            print('interval_a:', interval_a)
            break
    
    #find all the beats of the current interval
    for interval in grouped_beats_a.keys():
        if interval == interval_a:
            beats_a = grouped_beats_a[interval]
            print('beats_a:', beats_a)
            break

    #find the first beat of the interval AFTER the current time_stamp
    for beat in beats_a:
        if beat >= time_stamp_a:
            beat_time_stamp_a = beat
            print('beat_time_stamp_a:', beat_time_stamp_a)
            break

    
    #find the first interval of the next song where the bpm is around the same
    for interval in intervalsBPMS_b.keys():
        bpm_b = intervalsBPMS_b[interval]
        if (bpm_b - bpm_a) <= _BPM_ACCEPTED_MARGIN_IN_SECONDS:
            interval_b = interval
            print('interval_b:', interval_b)
            break
    
    #find the first beat of the next song's selected interval
    if not interval_b is None:
        #get first beat as transition timestamp 
        beat_time_stamp_b = grouped_beats_b[interval_b][0]
        print('beat_time_stamp_b:', beat_time_stamp_b)

    return (beat_time_stamp_a, beat_time_stamp_b)

def sortSongsByDominantBPM():
    bpmsBySong = {}
    for song in songs:
        print(song)
        intervals = getSongTimeIntervals(song)
        x,sr = librosa.load(song)
        tempo, beat_times = librosa.beat.beat_track(x, sr=sr,  units='time')
        groupedBeats =  groupBeats(beat_times, intervals)
        countedGroupedBeats =  countGroupedBeats(groupedBeats)
        intervalsBPMs = calcIntervalsBPMS(countedGroupedBeats)
        bpmFreqs =  getBPMFrequencies(intervalsBPMs)
        dominantBPM = getModeBPM(bpmFreqs)
        bpmsBySong[song] = dominantBPM
    
    sorted_songs = sorted(bpmsBySong.items(), key=operator.itemgetter(1))
    print("sorted songs:", sorted_songs)


def transitionTest():
    song_a = 'i_like_it_like_that.mp3'
    intervals_a = getSongTimeIntervals(song_a)
    x_a,sr_a = librosa.load(song_a)
    tempo_a, beat_times_a = librosa.beat.beat_track(x_a, sr=sr_a,  units='time')
    groupedBeats_a =  groupBeats(beat_times_a, intervals_a)
    #print('groupedBeats_a:', groupedBeats_a)
    countedGroupedBeats_a =  countGroupedBeats(groupedBeats_a)
    #print(groupedBeats_a)
    intervalsBPMs_a = calcIntervalsBPMS(countedGroupedBeats_a)

    song_b = 'mocca.mp3'
    intervals_b = getSongTimeIntervals(song_b)
    x_b,sr_b = librosa.load(song_b)
    tempo_b, beat_times_b = librosa.beat.beat_track(x_b, sr=sr_b,  units='time')
    groupedBeats_b = groupBeats(beat_times_b, intervals_b)
    countedGroupedBeats_b =  countGroupedBeats(groupedBeats_b)
    intervalsBPMs_b = calcIntervalsBPMS(countedGroupedBeats_b)

    start, end = getTransitionTimes(236.0, intervalsBPMs_a, groupedBeats_a, intervalsBPMs_b, groupedBeats_b)
    print(start, end)

    


def getModeBPM(bpmFreqs):
    mode = 0
    maxFreq = 0
    for bpm in bpmFreqs.keys():
        freq = bpmFreqs[bpm]
        if  freq >= maxFreq:
            mode = bpm
            maxFreq = freq
    
    return mode

def getBPMFrequencies(intervalsBPMs):
    bpmFreqs = {}
    for bpm in intervalsBPMs.values():
        if not bpm in bpmFreqs.keys():
            bpmFreqs[bpm] = 1
        else:
            bpmFreqs[bpm] = bpmFreqs[bpm] + 1
    return bpmFreqs

def calcIntervalsBPMS(beats_frequencies):
    intervalsBPMs = {}
    for interval in beats_frequencies.keys():
        start, end = interval
        beats = beats_frequencies[interval]
        bpm = calculateBPM(beats, start, end)
        intervalsBPMs[interval] = bpm
    return intervalsBPMs

def groupBeats(beat_times, intervals):
    beatsByInterval = {}
    for interval in intervals:
        start, end = interval
        beats = []
        for beat_time in beat_times:
            if beat_time > start and beat_time <= end:
                beats.append(beat_time)
        beatsByInterval[interval] = beats
    
    return beatsByInterval

def countGroupedBeats(groupedBeats):
    countedBeatsByInterval = {}

    for interval in groupedBeats.keys():
        countedBeatsByInterval[interval] = len(groupedBeats[interval])

    return countedBeatsByInterval

def getSongTimeIntervals(song_name):
    duration = getSongDuration(song_name)
    segments = numpy.arange(0, duration, _SEGMENTS_LENGTH_IN_SECONDS)
    intervals = []
    i = 0
    while(i < (len(segments) - 1) ):
        start = segments[i]
        end = segments[i + 1]
        intervals.append((start, end))
        i = i + 1

    last_segment = segments[len(segments) - 1]
    intervals.append((last_segment, duration))

    return intervals


def getSongTempo(song_name):
    x,sr = librosa.load(song_name)
    tempo, beat_times1 = librosa.beat.beat_track(x, sr=sr,  units='time')
    return tempo

def getSongDuration(song_name):
    mp3 = MP3(song_name)
    return mp3.info.length

def main():
    #dominantBPMMethod()
    transitionTest()

def calculateBPM(beats, start, end):
    bpm = (beats * 60)/(end - start)
    return bpm

if __name__ == '__main__':
    main()
