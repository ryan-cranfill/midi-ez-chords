<template>
  <v-container>
    <v-layout
      text-center
      column
    >
      <v-flex>
        <v-radio-group v-model="selectedFret" row>
          <v-radio label="Open" value="0"></v-radio>
          <v-radio v-for="n in 12" :label="`Fret ${n}`" :value="n" :key="n"></v-radio>
        </v-radio-group>
      </v-flex>
      <v-flex>
        <h1>Fret {{ selectedFret }}</h1>
        <v-select
            :items="midiInputs"
            v-model="selectedInput"
            label="Select MIDI Input"
            @change="inputChanged"
        ></v-select>
      </v-flex>
      <v-flex>
        <v-layout row>
          <v-flex xs2>
            <v-checkbox v-model="selectedNotes" label="String 1 (E)" :value="1"></v-checkbox>
            <v-checkbox v-model="selectedNotes" label="String 2 (b)" :value="2"></v-checkbox>
            <v-checkbox v-model="selectedNotes" label="String 3 (g)" :value="3"></v-checkbox>
            <v-checkbox v-model="selectedNotes" label="String 4 (d)" :value="4"></v-checkbox>
            <v-checkbox v-model="selectedNotes" label="String 5 (a)" :value="5"></v-checkbox>
            <v-checkbox v-model="selectedNotes" label="String 6 (e)" :value="6"></v-checkbox>
            {{ selectedNotes }}
          </v-flex>
          <v-flex xs2>
            <v-text-field :value="notes[1]" v-model="notes[1]"></v-text-field> {{ midiToNoteName(notes[1]) }}
            <v-text-field :value="notes[2]" v-model="notes[2]"></v-text-field> {{ midiToNoteName(notes[2]) }}
            <v-text-field :value="notes[3]" v-model="notes[3]"></v-text-field> {{ midiToNoteName(notes[3]) }}
            <v-text-field :value="notes[4]" v-model="notes[4]"></v-text-field> {{ midiToNoteName(notes[4]) }}
            <v-text-field :value="notes[5]" v-model="notes[5]"></v-text-field> {{ midiToNoteName(notes[5]) }}
            <v-text-field :value="notes[6]" v-model="notes[6]"></v-text-field> {{ midiToNoteName(notes[6]) }}
            {{ notes }}
          </v-flex>
          <v-flex xs8>
            Hey this is where the note selection stuff goes
          </v-flex>
        </v-layout>
      </v-flex>
      <v-flex>
        Hey this is where the submit and name button goes
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import webmidi from 'webmidi';
  import mpeInstrument from 'mpe';
  import MIDIMessage from 'midimessage';
  import { midiToNoteName } from "@tonaljs/midi";

  const instrument = mpeInstrument({pitch: true});
  // instrument.subscribe(console.log);

  export default {
    data: () => ({
      selectedFret: 0,
      selectedNotes: [],
      notes: {
        1: 24,
        2: 31,
        3: 36,
        4: 40,
        5: 43,
        6: 48
      },
      midiInputs: [],
      selectedInput: null
    }),
    methods: {
      midiToNoteName,
      inputChanged: function () {
        // EventBus.$emit('inputChanged', {output: this.selectedOutput})
      },
      setUpMidi: function () {
        let midiInputs = [];
        webmidi.enable(function (err) {
          if (err) {
            console.log("WebMidi could not be enabled.", err);
          } else {
            console.log("WebMidi enabled!");
          }
        });

        navigator.requestMIDIAccess().then(access => {
        // Iterate over the list of inputs returned
          access.inputs.forEach(midiInput => {
            midiInputs.push(midiInput.name);
              // Send 'midimessage' events to the mpe.js `instrument` instance
            midiInput.addEventListener(
              'midimessage',
              event => {
                if (event.srcElement.name !== this.selectedInput) return;
                  // if (event.srcElement.name === 'IAC Driver Bus 1') {
                let message = MIDIMessage(event);
                instrument.processMidiMessage(event.data);
                // console.log(instrument);
                console.log(message);
                if (message.messageType === 'noteon'){
                  // console.log(message);
                  this.selectedNotes.forEach(n => {
                    this.notes[n] = message.key
                  })
                }
                  // }
                // this.sendMidiState()
              }
            );
          });
        });
        // EventBus.$emit('newMidiInputs', {'inputNames': midiInputs})
        this.midiInputs = midiInputs;
      }
    },
    mounted() {
      this.setUpMidi();
    }
};
</script>
