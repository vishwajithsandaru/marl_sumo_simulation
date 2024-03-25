from typing import List
import numpy as np
from sumo_rl.environment.observations import ObservationFunction
from sumo_rl.environment.traffic_signal import TrafficSignal
from edge_info import key_exists, get_routes, get_containing_edges

from gymnasium import spaces


class PrioratizingObs(ObservationFunction):

    def __init__(self, ts: TrafficSignal):
        """Initialize default observation function."""
        super().__init__(ts)

    def get_routes_density(self) -> List[float]:
        """Returns the density [0,1] of the vehicles in the incoming lanes of the intersection.

        Obs: The density is computed as the number of vehicles divided by the number of vehicles that could fit in the lane.
        """
        routes = get_routes(self.ts.id)

        routes_density = []

        for route in routes:
            edges = get_containing_edges(ts_id=self.ts.id, route_id=route)
            total_vehicle_count = 0
            route_length = 0
            last_step_length = 0

            for edge in edges:
                total_vehicle_count += self.ts.sumo.edge.getLastStepVehicleNumber(edge)
                route_length += self.ts.sumo.lane.getLength(edge+'_0')
                last_step_length += self.ts.MIN_GAP + self.ts.sumo.edge.getLastStepLength(edge)

            density = total_vehicle_count / (route_length / last_step_length)
            routes_density.append(density)

        return [min(1, density) for density in routes_density]


        

    def get_routes_queue(self) -> List[float]:
        """Returns the queue [0,1] of the vehicles in the incoming lanes of the intersection.

        Obs: The queue is computed as the number of vehicles halting divided by the number of vehicles that could fit in the lane.
        """
        routes = get_routes(self.ts.id)

        routes_queue = []

        for route in routes:
            edges = get_containing_edges(ts_id=self.ts.id, route_id=route)
            total_halted_vehicle_count = 0
            route_length = 0
            last_step_length = 0

            for edge in edges:
                total_halted_vehicle_count += self.ts.sumo.edge.getLastStepHaltingNumber(edge)
                route_length += self.ts.sumo.lane.getLength(edge+'_0')
                last_step_length += self.ts.MIN_GAP + self.ts.sumo.edge.getLastStepLength(edge)

            queue = total_halted_vehicle_count / (route_length / last_step_length)
            routes_queue.append(queue)
        return [min(1, queue) for queue in routes_queue]


    def _one_hot_enc_max_mb_count(self) -> int:
        _lanes = self.ts.lanes
        counts = []
        for _lane in _lanes:
            vehicle_list = self.ts.sumo.lane.getLastStepVehicleIDs(_lane)
            motorbike_count = sum(1 for vehicle in vehicle_list if self.ts.sumo.vehicle.getTypeID(vehicle) == 'motorbike' and self.ts.sumo.vehicle.getSpeed(vehicle) <= 0.2)
            counts.append(motorbike_count)

        max_val = max(counts)
        max_index = counts.index(max_val)

        lane_representation = [0] * len(_lanes)
        
        if max_val != 0:
            lane_representation[max_index] = 1

        return lane_representation
    
    def _one_hot_enc_max_mb_count_route(self) -> int:
        
        route_mb_count = []

        routes = get_routes(self.ts.id)

        for route in routes:
            mb_count = 0
            edges = get_containing_edges(ts_id=self.ts.id, route_id=route)
            for edge in edges:
                vehicle_list = self.ts.sumo.edge.getLastStepVehicleIDs(edge)
                _mb_count = sum(1 for vehicle in vehicle_list if self.ts.sumo.vehicle.getTypeID(vehicle) == 'motorbike' and self.ts.sumo.vehicle.getSpeed(vehicle) <= 0.2)
                mb_count += _mb_count
            route_mb_count.append(mb_count)
        
        max_val = max(route_mb_count)
        if(self.ts.id == 'pepiliyana_jnct'):
            print('Route mb count: ', route_mb_count)
        max_index = route_mb_count.index(max_val)

        route_representation = [0] * len(routes)
        if max_val != 0:
            route_representation[max_index] = 1

        return route_representation
        

    def __call__(self) -> np.ndarray:
        """Customzed observation to include two-wheeler details"""

        phase_id = [1 if self.ts.green_phase == i else 0 for i in range(self.ts.num_green_phases)]  # one-hot encoding
        min_green = [0 if self.ts.time_since_last_phase_change < self.ts.min_green + self.ts.yellow_time else 1]        

        density = []
        queue = []
        mb_traffic_lane_representation = []

        if key_exists(self.ts.id):
            density = self.get_routes_density()
            queue = self.get_routes_queue()

            mb_traffic_lane_representation = self._one_hot_enc_max_mb_count_route()
            # print('-----------start------------')
            # print('Route Density: ', density)
            # print('Route Queue: ', queue)
            # print('------------end------------')
            if(self.ts.id == 'pepiliyana_jnct'):
                # print('-----------start------------')
                print('MB traffic lane representation: ', mb_traffic_lane_representation)
                # print('------------end------------')

        else:
            density = self.ts.get_lanes_density()
            queue = self.ts.get_lanes_queue()

            mb_traffic_lane_representation = self._one_hot_enc_max_mb_count()

        observation = np.array(phase_id + min_green + density + queue + mb_traffic_lane_representation, dtype=np.float32)
        return observation

    def observation_space(self) -> spaces.Box:
        """Return the observation space."""

        if key_exists(self.ts.id):
            _routes = get_routes(self.ts.id)
            return spaces.Box(
                low=np.zeros(self.ts.num_green_phases + 1 + 3 * len(_routes), dtype=np.float32),
                high=np.ones(self.ts.num_green_phases + 1 + 3 * len(_routes), dtype=np.float32),
            )
        else:
            return spaces.Box(
                low=np.zeros(self.ts.num_green_phases + 1 + 3 * len(self.ts.lanes), dtype=np.float32),
                high=np.ones(self.ts.num_green_phases + 1 + 3 * len(self.ts.lanes), dtype=np.float32),
            )

    
    