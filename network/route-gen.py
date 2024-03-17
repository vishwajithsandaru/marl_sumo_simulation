import random

def generate_traffic_flows():
    routes = [
        "attidiya_kohuwela", "attidiya_mirihana", "attidiya_nugegoda", "attidiya_piliyandala",
        "dehiwala_kohuwela", "dehiwala_nugegoda", "dehiwala_pannipitiya", "delkanda_piliyandala",
        "jubilee_post_pannipitiya", "kohuwela_attidiya", "kohuwela_delkanda", "kohuwela_pannipitiya",
        "kohuwela_piliyandala", "mirihana_kohuwela", "mirihana_nugegoda", "mirihana_pannipitiya",
        "nugegoda_delkanda_piliyandala", "nugegoda_jubilee_post", "nugegoda_mirihana", "nugegoda_pannipitiya",
        "nugegoda_piliyandala", "pannipitiya_mirihana", "pannipitiya_nugegoda", "pannipitiya_piliyandala",
        "pepiliyana_delkanda", "pepiliyana_piliyandala", "piliyandala_dehiwala", "piliyandala_kohuwela", "piliyandala_mirihana", "piliyandala_nugegoda", "piliyandala_pepiliyana_nugegoda"
    ]

    with open("traffic_flows.txt", "w") as file:
        for route in routes:
            car_flow = random.randint(50, 100)
            bike_flow = random.randint(50, 100) if route.startswith("attidiya_") or route.startswith("dehiwala_") else car_flow
            # Ensure car count is below 500
            if car_flow > 200:
                car_flow = 200
            # Ensure bike count is greater than car count if route starts with "attidiya_" or "dehiwala_"
            if route.startswith("attidiya_") or route.startswith("dehiwala_"):
                if bike_flow <= car_flow:
                    bike_flow = car_flow + random.randint(1, 100)
            else:
                if car_flow <= bike_flow:
                    car_flow = bike_flow + random.randint(1, 100)
            # Write flows to file
            file.write(f'<flow id="{route}_car" type="motorcar" begin="0" route="{route}" end="3600" vehsPerHour="{car_flow}"/>\n')
            file.write(f'<flow id="{route}_bike" type="motorbike" begin="0" route="{route}" end="3600" vehsPerHour="{bike_flow}"/>\n')

if __name__ == "__main__":
    generate_traffic_flows()
