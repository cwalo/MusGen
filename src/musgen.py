from mingus.containers import NoteContainer, Note, Bar, Track, Composition
import mingus.midi.midi_file_out as MidiFile
import mingus.core.chords as chords
import mingus.core.intervals as intervals
import mingus.core.progressions as progressions
from random import random, choice

class Key():
    C = "C"
    Cs = "C#"
    D = "D"
    Eb = "Eb"
    E = "E"
    F = "F"
    Fs = "F#"
    G = "G"
    Gs = "G#"
    Ab = "Ab"
    A = "A"
    As = "A#"
    Bb = "Bb"
    B = "B"

class Chord():
    I = "I"
    i = "Im"
    II = "II"
    ii = "IIm"
    iidim = "IIim"
    III = "III"
    iii = "IIIm"
    IV = "IV"
    iv = "IVm"
    V = "V"
    v = "Vm"
    VI = "VI"
    vi = "VIm"
    VII = "VII"
    vii = "VIIm"
    viidim = "VIIdim"

# Scale
class Scale():
    Major = 0
    Minor = 1

class ProgressionPart:
    def __init__(self, chord, scale, key):
        self.chord = chord
        self.scale = scale
        self.key = key

    def next(self):
        options = []

        if self.scale == Scale.Major:
            # Major RULES
            if self.chord == Chord.I:
                options = [Chord.I, Chord.ii, Chord.iii, Chord.IV, Chord.V, Chord.vi, Chord.viidim]
            elif self.chord == Chord.ii:
                options = [Chord.viidim, Chord.V] 
            elif self.chord == Chord.iii:
                options = [Chord.IV, Chord.vi]
            elif self.chord == Chord.IV:
                options = [Chord.I, Chord.ii, Chord.V, Chord.viidim]
            elif self.chord == Chord.V:
                options = [Chord.I, Chord.vi]
            elif self.chord == Chord.vi:
                options = [Chord.IV, Chord.ii, Chord.V]
            elif self.chord == Chord.viidim:
                options = [Chord.V, Chord.I]
        else:
            # Minor RULES
            if self.chord == Chord.i:
                options = [Chord.i, Chord.iidim, Chord.III, Chord.iv, Chord.v, Chord.VI, Chord.viidim]
            elif self.chord == Chord.iidim:
                options = [Chord.v, Chord.viidim] 
            elif self.chord == Chord.III:
                options = [Chord.iv, Chord.VI]
            elif self.chord == Chord.iv:
                options = [Chord.i, Chord.iidim, Chord.v, Chord.viidim]
            elif self.chord == Chord.v:
                options = [Chord.i, Chord.VI]
            elif self.chord == Chord.VI:
                options = [Chord.iidim, Chord.iv, Chord.v]
            elif self.chord == Chord.viidim:
                options = [Chord.v, Chord.i]

        return ProgressionPart(choice(options), self.scale, self.key)

progressionLength = 12
key = Key.G
meter = (4,4) 
scale = Scale.Major
firstScalechord = Chord.I

## Buffer
progression = []

## Create the progression
for i in range(progressionLength):
    if len(progression) == 0:
        firstChord = ProgressionPart(firstScalechord, scale, key)
        progression.append(firstChord)
    else:
        lastChord = progression[-1]
        nextChord = lastChord.next()
        progression.append(nextChord)

## Convert to MIDI
flatList = []
for part in progression:
    modChord = part.chord

    # random chord substitution
    if random() > 0.9:
        substitutions = progressions.substitute(modChord, 0)
        #modChord = choice(substitutions)
    
    flatList.append(modChord)

print(flatList)

builtChords = progressions.to_chords(flatList, key)

## Create bars for each chord
comp = []
lead = []

for chord in builtChords:
    modChord = chord

    #randomly invert before adding
    if random() > 0.7: # and randVal < 0.8:
        modChord = chords.second_inversion(modChord)
    elif random() > 0.7:
        modChord = chords.third_inversion(modChord)

    container = NoteContainer(modChord)

    #write a melody
    leadBar = Bar(key, meter)
    noteLengths = [2,4,8]
    lastNote = Note()
    lastNoteLength = 4

    while leadBar.is_full() == False:
        if random() < 0.8:
            currentBeat = leadBar.current_beat
            # add a note
            # if random() < 0.5 and len(leadBar) > 0:
            #     n = Note(intervals.second(lastNote.name, key))
            #     print("second of last")
            if random() < 0.5 and currentBeat != 0.0:
                n = Note(intervals.second(choice(container).name, key))
                # print("second")
            elif random() < 0.5 and currentBeat != 0.0:
                n = Note(intervals.seventh(choice(container).name, key))
                # print("seventh")
            else:
                n = Note(choice(container).name)
                # print("in chord")
            
            lastNote = n
            lastNoteLength = choice(noteLengths)

            leadBar.place_notes(n, lastNoteLength)
        else:
            # add a rest
            leadBar.place_rest(choice(noteLengths))

    lead.append(leadBar)

    for note in container:
        note = note.octave_down()

    noteLengths = [1]
    bar = Bar(key, meter)
    bar.place_notes(container, choice(noteLengths))
    comp.append(bar)

track = Track()
for bar in comp:
    track.add_bar(bar)

leadTrack = Track()
for bar in lead:
    leadTrack.add_bar(bar)


composition = Composition()
composition.add_track(track)
# composition.add_track(leadTrack)

MidiFile.write_Composition("musgen.mid", composition)
MidiFile.write_Track("musgenLead.mid", leadTrack)

