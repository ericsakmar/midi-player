import mido

class Midi:
    def __init__(self):
        output_port_names = mido.get_output_names()
        output_port_name = [p for p in output_port_names if 'MIDI 2' in p][0]
        self.output_port = mido.open_output(output_port_name)

        input_port_names = mido.get_input_names() 
        input_port_name = [p for p in output_port_names if 'MIDI 1' in p][0]
        self.input_port = mido.open_input(input_port_name)

    def close(self):
        self.output_port.close()
        self.input_port.close()
