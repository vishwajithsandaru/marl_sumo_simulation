from typing import List
from sumo_rl.environment.traffic_signal import TrafficSignal
from edge_info import key_exists, get_routes, get_containing_edges


def get_custom_accumulated_waiting_time_per_lane(ts: TrafficSignal, mb_weight: float = 2.0) -> List[float]:
        wait_time_per_lane = []
        for lane in ts.lanes:
            veh_list = ts.sumo.lane.getLastStepVehicleIDs(lane)
            wait_time = 0.0
            for veh in veh_list:
                veh_lane = ts.sumo.vehicle.getLaneID(veh)
                acc = ts.sumo.vehicle.getAccumulatedWaitingTime(veh)
                if veh not in ts.env.vehicles:
                    ts.env.vehicles[veh] = {veh_lane: acc}
                else:
                    ts.env.vehicles[veh][veh_lane] = acc - sum(
                        [ts.env.vehicles[veh][lane] for lane in ts.env.vehicles[veh].keys() if lane != veh_lane]
                    )
                is_motorbike = ts.sumo.vehicle.getTypeID(veh) == "motorbike"
                wait_time += ts.env.vehicles[veh][veh_lane] * (mb_weight if is_motorbike else 1.0)
            wait_time_per_lane.append(wait_time)
        return wait_time_per_lane



def calculate_custom_accumulated_waiting_time(ts: TrafficSignal, motorbike_weight: float = 2.0) -> List[float]:
    accumulated_waiting_time_per_lane = []

    for lane in ts.lanes:
        vehicle_list = ts.sumo.lane.getLastStepVehicleIDs(lane)
        lane_waiting_time = 0.0
        for vehicle in vehicle_list:
            vehicle_lane = ts.sumo.vehicle.getLaneID(vehicle)
            accumulated_time = ts.sumo.vehicle.getAccumulatedWaitingTime(vehicle)

            if vehicle not in ts.env.vehicles:
                ts.env.vehicles[vehicle] = {vehicle_lane: accumulated_time}
            else:
                ts.env.vehicles[vehicle][vehicle_lane] = accumulated_time - sum(
                    [ts.env.vehicles[vehicle][prev_lane] for prev_lane in ts.env.vehicles[vehicle].keys() if prev_lane != vehicle_lane]
                )

            is_motorbike = ts.sumo.vehicle.getTypeID(vehicle) == "motorbike"
            lane_waiting_time += ts.env.vehicles[vehicle][vehicle_lane] * (motorbike_weight if is_motorbike else 1.0)

        accumulated_waiting_time_per_lane.append(lane_waiting_time)

    return accumulated_waiting_time_per_lane


def calculate_route_accumulated_waiting_time(ts: TrafficSignal, motorbike_weight: float = 2.0) -> List[float]:
     
    routes = get_routes(ts_id=ts.id)
    accumulated_waiting_time_per_route = []

    for route in routes:
        edges = get_containing_edges(route_id=route)
        accumulated_waiting_time_of_edges = 0
        for edge in edges:
            vehicle_list = ts.sumo.edge.getLastStepVehicleIDs(edge)
            acc_waiting_time_of_edge = 0
            for vehicle in vehicle_list:
                waiting_time = ts.sumo.vehicle.getWaitingTime(vehicle)

                if vehicle in ts.env.vehicle_route and route in ts.env.vehicle_route[vehicle]:
                    ts.env.vehicle_route[vehicle][route] += waiting_time
                    waiting_time = ts.env.vehicle_route[vehicle][route] 
                else:
                    ts.env.vehicle_route[vehicle][route] = waiting_time
                acc_waiting_time_of_edge += waiting_time
            accumulated_waiting_time_of_edges += acc_waiting_time_of_edge
        
        accumulated_waiting_time_per_route.append(accumulated_waiting_time_of_edges)

    return accumulated_waiting_time_per_route

def custom_waiting_time_reward(ts: TrafficSignal):
        
        ts_wait = sum(calculate_route_accumulated_waiting_time(ts)) / 100.0 if key_exists(ts.id) else sum(calculate_custom_accumulated_waiting_time(ts)) / 100.0
        # print("Last Measure: ", ts.last_measure)
        # print("TS Wait: ", ts_wait)
        reward = ts.last_measure - ts_wait

        # print("Reward: ", reward)
        ts.last_measure = ts_wait
        return reward