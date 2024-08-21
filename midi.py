import mido
import logging

class Midi:
    def __init__(self):
        try:
            output_port_names = mido.get_output_names()
            output_port_name = [p for p in output_port_names if 'MIDI 2' in p][0]
            self.output_port = mido.open_output(output_port_name)
        except:
            logging.warning("Unable to connect to MIDI output")
            self.output_port = None


        try:
            input_port_names = mido.get_input_names() 
            input_port_name = [p for p in output_port_names if 'MIDI 1' in p][0]
            self.input_port = mido.open_input(input_port_name)
        except:
            logging.warning("Unable to connect to MIDI input")
            self.input_port = []

    def close(self):
        self.output_port.close()
        self.input_port.close()
