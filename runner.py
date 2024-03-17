import os
import sys
import sumolib
import traci
import pandas as pd
import numpy as np
from pathlib import Path

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit('SUMO_HOME is not defined.')

time_steps = 5000
net_file = "./network/colombo-suburbs.net.xml"
route_file = "./network/colombo-suburbs.rou.xml"
sumocfg_file = "./network/colombo-suburbs.sumocfg"
lateral_resolution = "0.3"
output_csv = "output/info.csv"
gui = False

metrics = []

def start():

    sumo_cmd = ""

    if not gui:
        sumo_cmd = ['sumo', '-n', net_file, '-r', route_file, '--lateral-resolution', lateral_resolution]
    else:
        sumo_binary = sumolib.checkBinary('sumo-gui')
        sumo_cmd = [sumo_binary, '-c', sumocfg_file]

    traci.start(sumo_cmd)
    
    for time_step in range(time_steps):
        traci.simulationStep()

        # Getting system info
        info = {'step': traci.simulation.getTime()}
        info.update(get_system_info())

        metrics.append(info.copy())
        print(f'Current Step: {traci.simulation.getTime()}', end='\r')

    df = pd.DataFrame(metrics)
    Path(Path(output_csv).parent).mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    traci.close()

def get_system_info():
    vehicles = traci.vehicle.getIDList()
    speeds_mc = []
    speeds_mb = []
    waiting_times_mc = [] 
    waiting_times_mb = []

    for vehicle in vehicles:
        if traci.vehicle.getTypeID(vehicle) == 'motorcar':
            # speeds_mc.append(traci.vehicle.getSpeed(vehicle))
            waiting_times_mc.append(traci.vehicle.getWaitingTime(vehicle))
        else:
            # speeds_mb.append(traci.vehicle.getSpeed(vehicle))
            waiting_times_mb.append(traci.vehicle.getWaitingTime(vehicle))
        

    return {
        # 'system_total_stopped_mc': sum(int(speed_mc < 0.1) for speed_mc in speeds_mc),
        # 'system_total_stopped_mb': sum(int(speed_mb < 0.1) for speed_mb in speeds_mb),
        # 'system_total_waiting_time_mc': sum(waiting_times_mc),
        # 'system_total_waiting_time_mb': sum(waiting_times_mb),
        # 'system_mean_speed_mc': 0.0 if len(vehicles) == 0 else np.mean(speeds_mc),
        # 'system_mean_speed_mb': 0.0 if len(vehicles) == 0 else np.mean(speeds_mb)
        'system_mean_waiting_time_mc': 0.0 if len(waiting_times_mc) == 0 else np.mean(waiting_times_mc),
        'system_mean_waiting_time_mb': 0.0 if len(waiting_times_mb) == 0 else np.mean(waiting_times_mb)
    }

if __name__ == "__main__":
    start()

