from typing import List


edge_info = {
    'pepiliyana_jnct':[
        '981161568#1', '981161568#0', '55090838#17', '55090838#16', '55090838#15', '55090838#14', '55090838#13', '55090838#12', '55090838#11', '55090838#9',
        '-161789385#1', '-161789385#3', '-161789385#4', '-161789385#5', '-161789385#6', '-161789385#7', '-161789385#8', '-161789385#9', '-557139526#0', '-557139526#1', '-557139526#2', '-557139526#3', '-557139526#4', '-557139526#5', '-557139526#6',
        '23323033#12', '23323033#11', '23323033#10', '23323033#9', '23323033#8', '23323033#6', '23323033#5',
        '771870128#6', '161783164#4', '161783164#3', '161783164#0'
    ]
}

def key_exists(ts_id: str) -> bool:
    if ts_id in edge_info:
        return True
    else:
        return False
    
def get_edges(ts_id: str) -> List:
    return edge_info[ts_id]

def get_lanes(ts) -> List:
    _lanes = []
    _edges = get_edges(ts_id=ts.id)
    for _edge in _edges:
        edge_lanes = ts.sumo.edge.getLanes(_edge)
        _lanes.extend(edge_lanes)
    return _lanes
