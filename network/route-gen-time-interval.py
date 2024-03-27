import random

routes = [
        "attidiya_kohuwela", "attidiya_mirihana", "attidiya_nugegoda", "attidiya_piliyandala",
        "dehiwala_kohuwela", "dehiwala_nugegoda", "dehiwala_pannipitiya", "delkanda_piliyandala",
        "jubilee_post_pannipitiya", "kohuwela_attidiya", "kohuwela_delkanda", "kohuwela_pannipitiya",
        "kohuwela_piliyandala", "mirihana_kohuwela", "mirihana_nugegoda", "mirihana_pannipitiya",
        "nugegoda_delkanda_piliyandala", "nugegoda_jubilee_post", "nugegoda_mirihana", "nugegoda_pannipitiya",
        "nugegoda_piliyandala", "pannipitiya_mirihana", "pannipitiya_nugegoda", "pannipitiya_piliyandala",
        "pepiliyana_delkanda", "pepiliyana_piliyandala", "piliyandala_dehiwala", "piliyandala_kohuwela", "piliyandala_mirihana", "piliyandala_nugegoda", "piliyandala_pepiliyana_nugegoda"
    ]

excluded_routes = ["kohuwela_delkanda", "nugegoda_piliyandala", "pepiliyana_piliyandala"]

motorbike_routes = [
    "attidiya_kohuwela", "attidiya_mirihana", "attidiya_nugegoda", "attidiya_piliyandala", "dehiwala_kohuwela", "dehiwala_pannipitiya",  "mirihana_kohuwela", "mirihana_pannipitiya", 
    "nugegoda_piliyandala", "pannipitiya_mirihana", "piliyandala_dehiwala", "piliyandala_nugegoda"
]

normal_time_intervals = ['0-200', '200-1000', '1000-2000', '2000-2500', '2500-3000', '3000-5000']
motorbike_time_intervals = ['0-200', '1000-2000', '2500-3000']

output_file_name = 'generated-flows.txt'

def generate_flow(route, vehicle_type, start_time, end_time, vehs_per_hour):
    flow_id = f"{route}_{vehicle_type}_{start_time}_{end_time}"
    begin = start_time
    end = end_time
    depart_speed = "max"
    depart_pos = "base"
    depart_lane = "best"
    vehs_per_hour = vehs_per_hour

    xml_tag = f'<flow id="{flow_id}" type="{vehicle_type}" begin="{begin}" route="{route}" end="{end}" departSpeed="{depart_speed}" departPos="{depart_pos}" departLane="{depart_lane}" vehsPerHour="{vehs_per_hour}"/>'
    return xml_tag

def generate_flows(routes, normal_time_intervals, motorbike_time_intervals, motorbike_routes):
    flows = []
    for interval in normal_time_intervals:
        start_time = interval.split('-')[0]
        end_time = interval.split('-')[1]
        # vehs_per_hour = random.randint(40, 80)
        for route in routes:
            vehs_per_hour = random.randint(40, 80)
            if route in excluded_routes:
                continue
            if interval in motorbike_time_intervals and route in motorbike_routes:
                vehicle_type = "motorbike"
            else:
                vehicle_type = "motorcar"
            flows.append(generate_flow(route, vehicle_type, start_time, end_time, vehs_per_hour*3 if interval in motorbike_time_intervals and route in motorbike_routes else vehs_per_hour))
        flows.append('\n')
    return flows


def save_flows_to_file(flows, filename):
    with open(filename, 'w') as file:
        for flow in flows:
            file.write(flow + '\n')


flows = generate_flows(routes, normal_time_intervals, motorbike_time_intervals, motorbike_routes)

save_flows_to_file(flows, output_file_name)
