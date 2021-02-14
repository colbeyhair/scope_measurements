import numpy as np
import pyvisa
import Rigol1000z
import datetime
import os
import time

seconds_since = lambda start_time: (datetime.datetime.now() - start_time).total_seconds()

def main():

    log_file_name = datetime.datetime.now().strftime("log_%Y%m%d%H%M%S.csv")


    # connect to scope
    print("Connecting to scope",flush=True)
    rm = pyvisa.ResourceManager()
    try:
        resource_name = [resource for resource in rm.list_resources() if "usb" in str(resource).lower()][0]
        scope_resource = rm.open_resource(resource_name)
        scope = Rigol1000z.Rigol1000z(scope_resource)
    except IndexError:
        raise IndexError("Scope not found.")

    log_data([
        "Time",
        "Input Voltage [V]",
        "Input Current [A]",
        "Output Voltage [V]",
        "Output Current [A]",
        "Input Power [W]",
        "Output Power [W]",
        "Power efficiency [pu]",
        ])

    # setup_scope(scope)

    offset_values = [0,0,0,0]
    arg = None
    while arg != "q":
        arg = input("\nq = quit\nc = calibrate\nblank = record data point\nt = interval recording (indefinitely)\nenter your selection: ")
        if arg == "q":
            break

        elif arg == "c":
            try:
                if calibration_complete:
                    confirmation = input("WARNING: calibration has already happened. Enter 'y' to overwrite calibration values: ")
                    if confirmation == "y":
                        print("Re-calibrating",flush=True)
                        offset_values = read_offset_values(scope)

                    else:
                        print("Skipping re-calibration",flush=True)
            except NameError:
                offset_values = read_offset_values(scope)
                calibration_complete = True

        elif arg == "":
            try:
                if calibration_complete:
                    record_data_point(scope, offset_values)
            except NameError:
                confirmation = input("WARNING: calibration not performed. Enter 'y' to use zero offset: ")
                if confirmation == "y":
                    print("Using zero offset as default calibration.",flush=True)
                    calibration_complete = True
                    record_data_point(scope, offset_values)

        elif arg == "t":
            period_s = None
            try:
                period_s = float(input("Enter the time interval in seconds (0=flood): "))
            except ValueError:
                print("Unable to parse input. Try again.")

            if period_s is not None:
                try:
                    if calibration_complete:
                        record_points_timer(scope, offset_values, period_s)
                except NameError:
                    confirmation = input("WARNING: calibration not performed. Enter 'y' to use zero offset: ")
                    if confirmation == "y":
                        print("Using zero offset as default calibration.",flush=True)
                        calibration_complete = True
                        record_points_timer(scope, offset_values, period_s)



def record_points_timer(scope, offset_values, period_s):
    last_record_time = datetime.datetime.now()
    while True:
        while seconds_since(last_record_time) < period_s:
            time.sleep(0.01)
        last_record_time = datetime.datetime.now()
        record_data_point(scope, offset_values)

def setup_scope(scope):
    scope.set_high_resolution_mode()


def make_single_acquisition(scope):
    scope.set_single_shot()

    while not scope.get_trigger_status() == "wait":
        time.sleep(0.02)
    scope.force()

    while scope.get_trigger_status() != "stop":
        time.sleep(0.02)




def read_offset_values(scope):
    make_single_acquisition(scope)
    offset_values = [
        np.mean(scope[1].get_data('norm')[1]),
        np.mean(scope[2].get_data('norm')[1]),
        np.mean(scope[3].get_data('norm')[1]),
        np.mean(scope[4].get_data('norm')[1]),
    ]

    print("Offset values: ")
    print("\n".join(map("{:.4f}".format,offset_values)))

    return offset_values



def record_data_point(scope,offset_values):
    # input power measurement
    t,voltage_in = scope[1].get_data()
    voltage_in = voltage_in - offset_values[0]

    current_in = np.array(scope[2].get_data()[1]) - offset_values[1]

    # output power measurement
    voltage_out = np.array(scope[3].get_data()[1]) - offset_values[2]
    current_out = np.array(scope[4].get_data()[1]) - offset_values[3]

    time_delta = t[1]-t[0]

    power_in = np.sum(np.multiply(voltage_in, current_in)) * time_delta
    power_out = np.sum(np.multiply(voltage_out, current_out)) * time_delta

    efficiency = power_out / power_in if np.abs(power_in) > 1e-3 else 0

    data_to_log = [
        datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        np.mean(voltage_in),
        np.mean(current_in),
        np.mean(voltage_out),
        np.mean(current_out),
        power_in,
        power_out,
        efficiency,
        ]

    print("\n\n" + "\t".join(map(str,data_to_log)) + "\n", flush=True)

    log_data(data_to_log)


def log_data(data):
    # decide file name the first time we write anything to the log
    try:
        if log_data._log_file_name:
            pass
    except AttributeError:
        log_data._log_file_name = datetime.datetime.now().strftime("log_%Y%m%d%H%M%S.csv")

        # create file
        with open(log_data._log_file_name,"w") as _:
            pass

    if not isinstance(data, str):
        data = ",".join(map(str,data))
    else:
        data = data.rstrip("\n")

    with open(log_data._log_file_name, "a") as log_file:
        log_file.write(data + "\n")


if __name__ == '__main__':
    main()
