# -*- coding: utf-8 -*-
from fsm import MealyMachine, State, TransitionError

_TCP_STATES = [
    'CLOSED',
    'LISTEN',
    'SYN_RCVD',
    'ESTABLISHED',
    'SYN_SENT',
    'FIN_WAIT_1',
    'FIN_WAIT_2',
    'TIME_WAIT',
    'CLOSING',
    'CLOSE_WAIT',
    'LAST_ACK',
]

_TCP_EVENTS = [
    'PASSIVE',
    'ACTIVE',
    'SYN',
    'SYNACK',
    'ACK',
    'RDATA',
    'SDATA',
    'FIN',
    'CLOSE',
    'TIMEOUT',
]

_ = {
    'none': u'Λ',
    'syn': '<syn>',
    'ack': '<ack>',
    'syn-ack': '<syn-ack>',
    'fin': '<fin>',
    'n': '<n>',
}


class TCPMachine(MealyMachine):
    def transition(self, input_value):
        """Transition to the next state."""
        current = self.current_state
        if current is None:
            raise TransitionError('Current state not set.')

        destination_state = current.get(input_value,
                                        current.default_transition)
        if destination_state is None:
            raise TransitionError('Cannot transition from state %r'
                                  ' on input %r.' % (current.name,
                                                     input_value))
        else:
            self.current_state = destination_state
        # Added associated variable
        if input_value == 'RDATA':
            assert current.name == 'ESTABLISHED'
            current.received_count += 1
        if input_value == 'SDATA':
            assert current.name == 'ESTABLISHED'
            current.sent_count += 1

# Initialize states
TCP_STATES = {state: State(state) for state in _TCP_STATES}
TCP_MACHINE = TCPMachine('TCP')
TCP_MACHINE.init_state = TCP_STATES['CLOSED']

# Setup FSM
TCP_STATES['CLOSED'][('PASSIVE', _['none'])] = TCP_STATES['LISTEN']
TCP_STATES['CLOSED'][('ACTIVE', _['syn'])] = TCP_STATES['SYN_SENT']
TCP_STATES['LISTEN'][('SYN', _['syn-ack'])] = TCP_STATES['SYN_RCVD']
TCP_STATES['LISTEN'][('CLOSE', _['none'])] = TCP_STATES['CLOSED']
TCP_STATES['SYN_SENT'][(('CLOSE'), _['none'])] = TCP_STATES['CLOSED']
TCP_STATES['SYN_SENT'][('SYN', _['syn-ack'])] = TCP_STATES['SYN_RCVD']
TCP_STATES['SYN_SENT'][('SYNACK', _['ack'])] = TCP_STATES['ESTABLISHED']
TCP_STATES['SYN_RCVD'][('ACK', _['none'])] = TCP_STATES['ESTABLISHED']
TCP_STATES['SYN_RCVD'][('CLOSE', _['fin'])] = TCP_STATES['FIN_WAIT_1']
TCP_STATES['ESTABLISHED'][('CLOSE', _['fin'])] = TCP_STATES['FIN_WAIT_1']
TCP_STATES['ESTABLISHED'][('FIN', _['ack'])] = TCP_STATES['CLOSE_WAIT']
TCP_STATES['ESTABLISHED'][('RDATA', _['n'])] = TCP_STATES['ESTABLISHED']
TCP_STATES['ESTABLISHED'][('SDATA', _['n'])] = TCP_STATES['ESTABLISHED']
TCP_STATES['FIN_WAIT_1'][('FIN', _['ack'])] = TCP_STATES['CLOSING']
TCP_STATES['FIN_WAIT_1'][('ACK', _['none'])] = TCP_STATES['FIN_WAIT_2']
TCP_STATES['FIN_WAIT_2'][('FIN', _['ack'])] = TCP_STATES['TIME_WAIT']
TCP_STATES['CLOSING'][('ACK', _['none'])] = TCP_STATES['TIME_WAIT']
TCP_STATES['TIME_WAIT'][('TIMEOUT', _['none'])] = TCP_STATES['CLOSED']
TCP_STATES['CLOSE_WAIT'][('CLOSE'), _['fin']] = TCP_STATES['LAST_ACK']
TCP_STATES['LAST_ACK'][('ACK', _['none'])] = TCP_STATES['CLOSED']
