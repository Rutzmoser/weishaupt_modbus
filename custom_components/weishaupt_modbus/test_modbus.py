"""Scan all possible modbus registers for a value and write them into the register.txt file"""

import asyncio

from pymodbus import ExceptionResponse, ModbusException, pymodbus_apply_logging_config
import pymodbus.client as ModbusClient


async def scan_registers(registers, register_read_function, *args, **kwargs):
    """
    Scan the registers using the given register_read_function
    and store the results in a dictionary which gets returned.
    """
    register_dict = {}
    for register in registers:
        try:
            rr = await register_read_function(register, *args, **kwargs)
            if len(rr.registers) > 0:
                register_dict[register] = rr.registers[0]
        except ModbusException as exc:
            print("Exception raised:", exc)
    return register_dict


async def main():  # noqa: D103
    pymodbus_apply_logging_config("DEBUG")
    host = "192.168.42.144"  # 10.10.1.225"
    port = 502
    client = ModbusClient.AsyncModbusTcpClient(
        host,
        port=port,
    )
    await client.connect()

    binary_out = []  # range(1, 10_000)
    binary_in = []  # range(10_001, 20_000)
    input_registers = range(30_001, 40_000)
    holding_registers = range(40_001, 50_000)

    binary_out_found = await scan_registers(
        binary_out, client.read_coils, 1, device_id=1
    )
    binary_in_found = await scan_registers(binary_in, client.read_coils, 1, device_id=1)
    input_registers_found = await scan_registers(
        input_registers, client.read_input_registers, device_id=1
    )
    holding_registers_found = await scan_registers(
        holding_registers, client.read_holding_registers, device_id=1
    )

    client.close()

    file = open(file="register.txt", mode="w", encoding="UTF-8")  # noqa: ASYNC230, PTH123

    file.write("Binary out:\n")
    for register, val in binary_out_found.items():
        file.write(f"{register};{val}\n")

    file.write("Binary in:\n")
    for register, val in binary_in_found.items():
        file.write(f"{register};{val}\n")

    file.write("Input Registers:\n")
    for register, val in input_registers_found.items():
        file.write(f"{register};{val}\n")

    file.write("Holding Registers:\n")
    for register, val in holding_registers_found.items():
        file.write(f"{register};{val}\n")

    return


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
