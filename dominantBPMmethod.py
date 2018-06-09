import librosa, librosa.display
import numpy
import operator
from mutagen.mp3 import MP3

_SEGMENTS_LENGTH_IN_SECONDS = 4
songs = ['flames.mp3', 'no_es_justo.mp3', 'i_like_it_like_that.mp3', 'mocca.mp3', 'borracha.mp3', 'peligrosa.mp3', 'ambiente.mp3' ]
#songs = ['flames.mp3']


def dominantBPMMethod():
    bpmsBySong = {}
    for song in songs:
        print(song)
        intervals = getSongTimeIntervals(song)
        x,sr = librosa.load(song)
        tempo, beat_times = librosa.beat.beat_track(x, sr=sr,  units='time')
        #print((intervals))
        #print(song, duration, tempo)
        groupedBeats =  groupBeats(beat_times, intervals)
        #print(groupedBeats)
        intervalsBPMs = calcIntervalsBPMS(groupedBeats)
        #print(intervalsBPMs)
        bpmFreqs =  getBPMFrequencies(intervalsBPMs)
        print(bpmFreqs)
        dominantBPM = getModeBPM(bpmFreqs)
        print(dominantBPM)
        bpmsBySong[song] = dominantBPM
    
    sorted_songs = sorted(bpmsBySong.items(), key=operator.itemgetter(1))
    print("sorted songs:", sorted_songs)

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
    frequencies = {}
    for interval in intervals:
        start, end = interval
        for beat_time in beat_times:
            if beat_time > start and beat_time <= end:
                if interval not in frequencies.keys():
                    frequencies[interval] = 1
                else:
                    frequencies[interval] = frequencies[interval] + 1

    
    return frequencies




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
    intervals.append((last_segment, None))

    return intervals


def getSongTempo(song_name):
    x,sr = librosa.load(song_name)
    tempo, beat_times1 = librosa.beat.beat_track(x, sr=sr,  units='time')
    return tempo

def getSongDuration(song_name):
    mp3 = MP3(song_name)
    return mp3.info.length

def main():
    dominantBPMMethod()

def calculateBPM(beats, start, end):
    bpm = (beats * 60)/(end - start)
    return bpm


if __name__ == '__main__':
    main()
