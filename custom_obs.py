import numpy as np
from sumo_rl.environment.observations import ObservationFunction
from sumo_rl.environment.traffic_signal import TrafficSignal

from gymnasium import spaces


class PrioratizingObs(ObservationFunction):

    def __init__(self, ts: TrafficSignal):
        """Initialize default observation function."""
        super().__init__(ts)

    def _one_hot_enc_max_mb_count(self) -> int:
        _lanes = self.ts.lanes
        counts = []
        for _lane in _lanes:
            vehicle_list = self.ts.sumo.lane.getLastStepVehicleIDs(_lane)
            motorbike_count = sum(1 for vehicle in vehicle_list if self.ts.sumo.vehicle.getTypeID(vehicle) == 'motorbike')
            counts.append(motorbike_count)

        # if self.ts.id=='pepiliyana_jnct':
        #     print('Lanes: ', _lanes)
        #     print('Çounts: ', counts)

        max_val = max(counts)
        max_index = counts.index(max_val)

        lane_representation = [0] * len(_lanes)
        
        if max_val != 0:
            lane_representation[max_index] = max_val

        return lane_representation

    def __call__(self) -> np.ndarray:
        """Customzed observation to include two-wheeler details"""

        phase_id = [1 if self.ts.green_phase == i else 0 for i in range(self.ts.num_green_phases)]  # one-hot encoding
        min_green = [0 if self.ts.time_since_last_phase_change < self.ts.min_green + self.ts.yellow_time else 1]        

        lane_representation = self._one_hot_enc_max_mb_count()

        # print(lane_representation)

        density = self.ts.get_lanes_density()
        queue = self.ts.get_lanes_queue()
        observation = np.array(phase_id + min_green + density + queue, dtype=np.float32)
        return observation

    def observation_space(self) -> spaces.Box:
        """Return the observation space."""
        return spaces.Box(
            low=np.zeros(self.ts.num_green_phases + 1 + 2 * len(self.ts.lanes), dtype=np.float32),
            high=np.ones(self.ts.num_green_phases + 1 + 2 * len(self.ts.lanes), dtype=np.float32),
        )
    
    