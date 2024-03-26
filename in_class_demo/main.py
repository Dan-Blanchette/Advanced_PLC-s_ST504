import time
from pymodbus.client import ModbusTcpClient


class PLC_Tag():
    def __init__(self, name, modbus_address, value):
        self.name = name
        self.modbus_address = modbus_address
        self.value = value


def connect_to_plc():
    print("Attempting to connect to PLC...")
    client = ModbusTcpClient('192.168.0.10', port='502')
    client.connect()
    print("Connection Status: ", client)
    return client


def disconnect_from_click_plc(client):
    print("disconnecting from client")
    client.close()

def pulse_stepper_motor(client):
    # create motor pulse object
    pulse_the_stepper_motor = PLC_Tag("pulse_the_stepper_motor", 16390, None)
    # turn on stepper motor pulse coil 16390
    write_modbus_coils(client, pulse_the_stepper_motor.modbus_address, True)
    # wait for a certain amount of time
    time.sleep(.03)
    # turn off stepper motor pulse coil 16390
    write_modbus_coils(client, pulse_the_stepper_motor.modbus_address, False)
    # wait for a certain amount of time
    time.sleep(.03)

def write_modbus_coils(client, coil_num, bool_val):
    result = None
    coil_num = (coil_num - 1)
    # pymodbus built in write coil function
    result = client.write_coil(coil_num, bool_val)
    print("Writing to coil: ", coil_num, "Value: ", result)

    return result


def read_modbus_coils(client, coil_address, coil_range = 1):
    result_list = []
    # allows you to compensate for the off by 1 addressing
    coil_address = (coil_address - 1)
    result = client.read_coils(coil_address, coil_range)

    result_list = result.bits[0:coil_range]

    # print("Filtered result of only necessary values", result_list)
    return result_list
    

def main():
    #client object to connect to PLC
    client = connect_to_plc()
    # read the auto selector switch input
    selector_switch_in_auto = PLC_Tag("selector switch in auto", 16385, None)
    selector_switch_in_hand = PLC_Tag("selector switch in hand", 16386, None)
    estop = PLC_Tag("E-Stop", 16387, None)

    # Stepper Motor Objects
    # Stepper Motor Pulsing
    stepper_motor_direction = PLC_Tag("Stepper Motor Direction", 16391, None)
    # predefine stepper motor direction to be False
    result = write_modbus_coils(client, 16391, False)

    while True:
        # Read all of the selector switch inputs and E-Stop settings
        selector_switch_list = read_modbus_coils(client, 16385, 3)
        # read our stepper motor direction and store in the
        # object's .value attribute
        stepper_motor_direction.value = read_modbus_coils(client, 
                                            stepper_motor_direction.modbus_address,
                                            number_of_coils = 1 
                                            )[0]

        # print(selector_switch_list)
        selector_switch_in_auto.value = selector_switch_list[0]
        selector_switch_in_hand.value = selector_switch_list[1]
        estop.value = selector_switch_list[2]

        # Debugging print statements
        print("----------------------------------")
        print(selector_switch_in_auto.name, ":", selector_switch_in_auto.value)
        print(selector_switch_in_hand.name, ":", selector_switch_in_hand.value)
        print(estop.name, ":", estop.value)
        print("-")
        print(stepper_motor_direction.name, ":", stepper_motor_direction.value)
        print("----------------------------------")

        # test our PLCTag class works
        stepper_motor_direction.value = not stepper_motor_direction.value
        write_modbus_coils(client, 
                           stepper_motor_direction.modbus_address, 
                           stepper_motor_direction.value
                           )
        time.sleep(1)
        # print(selector_switch_in_auto.name)
        # print(selector_switch_in_auto.modbus_address)
        # print(selector_switch_in_auto.value)

    # Disconnect from the click PLC
    disconnect_from_click_plc(client)


if __name__ == '__main__':
    main()
