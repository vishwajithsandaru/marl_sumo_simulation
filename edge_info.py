from typing import List

edge_info = {
    'pepiliyana_jnct':{
        'r_120_col_inbound': ['981161568#1', '981161568#0', '55090838#17', '55090838#16', '55090838#15', '55090838#14', '55090838#13', '55090838#12', '55090838#11', '55090838#9'],
        'r_delkanda_inbound': [ '-161789385#1', '-161789385#3', '-161789385#4', '-161789385#5', '-161789385#6', '-161789385#7', '-161789385#8', '-161789385#9', '-557139526#0', '-557139526#1', '-557139526#2', '-557139526#3', '-557139526#4', '-557139526#5', '-557139526#6',],
        'r_120_inbound': ['23323033#12', '23323033#11', '23323033#10', '23323033#9', '23323033#8', '23323033#6', '23323033#5'],
        'r_dehiwala_inbound': ['771870128#6', '161783164#4', '161783164#3', '161783164#0']
    },
    'gamsaba_jnct':{
        'r_highlevel_col_inbound': ['E2', '51064306#0', '50070021#2', '50070021#0'],
        'r_ethul_kotte_inbound': ['-E4'],
        'r_highlevel_inbound': ['-E3.150', '-E3', '-51064306#7', '-51064306#8', '-51064306#9', '-190918151#0'],
        'r_pepiliyana_inbound': ['E1.54', 'E1', '161789990#5', '161789990#2', 'E0', '557139526#7', '557139526#6', '557139526#5']
    },
    'raththanpitiya_jnct': {
        'r_120_pepiliyana_inbound': ['981161571#2', '981161570#13', '981161570#12', '981161570#11', '981161570#10', '981161570#9'],
        'r_120_inbound': ['557140714#1.13']
    },
    'delkanda_jnct': {
        'r_highlevel_gamsaba_jnct_inbound': ['190918151#3.59', '190918151#3', '190918151#2', '190918151#1', '51064306#10', '51064306#9', '51064306#8', '51064306#7'],
        'r_mirihana_inbound': ['23185504#5.93', '23185504#5', '23185504#4', '23185504#3', '23185504#2', '23185504#1', '23185504#0'],
        'r_highlevel_inbound': ['-190918151#4', '-131349573', '-131349574#1', '-131349574#3'],
        'r_raththanpitiya_jnct_inbound': ['-23351957#1.149', '-23351957#1', '-23351957#2', '-23351957#3', '-23351957#4', '-23351957#5']
    }
}

def key_exists(ts_id: str) -> bool:
    if ts_id in edge_info:
        return True
    else:
        return False
    
def get_routes(ts_id: str) -> List:
    return edge_info[ts_id]

def get_containing_edges(ts_id, route_id) -> List:
    return edge_info[ts_id][route_id]

# def get_lanes(ts) -> List:
#     _lanes = []
#     _edges = get_edges(ts_id=ts.id)
#     for _edge in _edges:
#         edge_lanes = ts.sumo.edge.getLanes(_edge)
#         _lanes.extend(edge_lanes)
#     return _lanes
