from __future__ import annotations
import mido
from random import randint
from threading import Thread, Event
from tinydb import TinyDB
from time import sleep


DB_PATH = 'mappings.json'

INPUT_NAME = 'Sensel Morph'
OUTPUT_NAME = 'Software Bus Bus 1'

thread_stop_event = Event()

CHORD_DEGREES = [0, 7, 12, 16, 19, 24]
# base notes: C-1, C#-1, D-1, D#-1, B0, F1, G2, G#2, A3, A#3, B4, C5, C#6, D6
BASE_NOTES = [12, 13, 14, 15, 35, 41, 55, 56, 69, 70, 83, 84, 97, 98]


def get_random_notes():
    return [randint(24, 100) for _ in CHORD_DEGREES]


class ChordMapping:
    def __init__(self, base_note=0, new_notes=None):
        if not new_notes:
            new_notes = get_random_notes()

        assert len(new_notes) == len(CHORD_DEGREES)

        self.base_notes = [base_note + degree for degree in CHORD_DEGREES]
        self.mapping = {
            base: new
            for base, new in zip(self.base_notes, new_notes)
        }

    def update(self, new: [dict, ChordMapping]):
        if isinstance(new, dict):
            self.mapping.update(new)
        elif isinstance(new, ChordMapping):
            self.mapping.update(new.mapping)
        else:
            raise TypeError('must be a dict or ChordMapping')

    def __iter__(self):
        return iter(self.mapping)

    def __getitem__(self, item):
        return self.mapping[item]

    def __repr__(self):
        return f'Mapping: {self.mapping}'


class ChordHandler(Thread):
    db = TinyDB(DB_PATH)
    delay = 0.001

    def __init__(self):
        input_names = mido.get_input_names()
        output_names = mido.get_output_names()

        chord_mappings = [ChordMapping(base_note=i) for i in BASE_NOTES]
        self.chord_mapping = ChordMapping(BASE_NOTES[0])
        for mapping in chord_mappings:
            self.chord_mapping.update(mapping)

        # inport_name = input_names[0]
        # outport_name = output_names[1]
        inport_name, outport_name = INPUT_NAME, OUTPUT_NAME
        print('connecting input {} and output {}'.format(inport_name, outport_name))
        self.inport = mido.open_input(inport_name)
        self.outport = mido.open_output(outport_name)
        print(self.inport)

        super(ChordHandler, self).__init__()

    def listen_for_messages(self):
        """
        Listens for midi messages. On receipt modifies them and then sends them out to the output bus
        """
        while not thread_stop_event.isSet():
            for message in self.inport:
                if 'note' in message.type:
                    new_message = self.handle_message(message)
                    print(message, new_message)
                    self.outport.send(new_message)
            sleep(self.delay)

    def handle_message(self, message: mido.messages.messages.Message):
        """
        Handle a new midi message
        :param message:
        :return:
        """
        base_note = message.note
        if base_note in self.chord_mapping:
            new_note = self.chord_mapping[base_note]
            message.note = new_note
        return message

    def handle_mapping(self, mapping):
        """
        Handle a new mapping being sent
        :param mapping:
        :return:
        """
        self.chord_mapping.update(mapping)
        print(mapping, self.chord_mapping)

    def run(self):
        self.listen_for_messages()

