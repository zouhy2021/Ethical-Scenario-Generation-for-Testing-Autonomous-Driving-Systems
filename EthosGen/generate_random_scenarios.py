import random
import pandas as pd

result_file = "scenario_result/random_logical_scenarios_mmfn.xlsx"

scenario_example = ("def scenario(): \n"
                    "    road_type = \"Straight Road\"\n"
                    "    environment = \"rainy\"\n"
                         "    ego_vehicle = vehicle(lane_id=1 , initial_speed=7 , direction=1) \n"
                         "    vehicle1 = vehicle(lane_id=1, distance= , initial_speed=7, direction=1) \n"
                         "    cyclist1 = cyclist(lane_id=1, distance= , initial_speed=7, direction=1) \n"
                         "    pedestrian1 = pedestrian(age= , gender= , distance= , initial_speed=4, direction=1) \n"
                         )

road_types = ['Intersection','T-junction','Straight Road','Multi-way Junction','Urban Road','Two-way Street','Multi-lane Road']
environments = ['Night','Daytime','Rainy','Sunny','Foggy','Slippery Road','Normal Road']
ages = ['Child','Young Adult','Old']
genders = ['Male','Female']
rear_vehicle_distance_range = [-20, -8] # mmfn:[-20, -8] wor:[-16, -6.5]  if: [-16, -8]
crossing_pedestrian_distance_range = [12, 20] # mmfn:[12, 20] wor:[10, 20]  if: [6, 20]
roadside_pedestrian_distance_range = [6.11, 9] # mmfn:[6.11, 9] wor:[6.11, 7]  if:[2.11, 3]
adjacent_cyclist_distance_range = [0, 12]
parked_vehicle_distance_range = [0, 3] # mmfn: [0, 3] wor:[0, 3]  if:[-2, -1]

all_results = []
# type1 的随机化生成
for i in range(1,2):
    pedestrian_num = 0
    vehicle_num = 0
    scenario = "def scenario(): \n"
    road_type = random.choice(road_types)
    scenario = scenario + f"    road_type = \"{road_type}\"\n"
    environment = random.choice(environments)
    scenario = scenario + f"    environment = \"{environment}\"\n"
    scenario = scenario + "    ego_vehicle = vehicle(lane_id=1, initial_speed=7, direction=1) \n"

    vehicle_num += 1
    rear_vehicle_distance = random.uniform(rear_vehicle_distance_range[0],rear_vehicle_distance_range[1])
    scenario = scenario + f"    vehicle{vehicle_num} = vehicle(lane_id=1, distance={rear_vehicle_distance}, initial_speed=7, direction=1) \n"

    if random.choice([True, False]):
        vehicle_num += 1
        parked_vehicle_distance = random.uniform(parked_vehicle_distance_range[0],parked_vehicle_distance_range[1])
        scenario = scenario + f"    vehicle{vehicle_num} = vehicle(lane_id=0, distance={parked_vehicle_distance}, initial_speed=0, direction=1) \n"

    if random.choice([True, False]):
        adjacent_cyclist_distance = random.uniform(adjacent_cyclist_distance_range[0],adjacent_cyclist_distance_range[1])
        scenario = scenario + f"    cyclist1 = cyclist(lane_id=2, distance={adjacent_cyclist_distance}, initial_speed=7, direction=1) \n"

    crossing_pedestrian_distance = random.uniform(crossing_pedestrian_distance_range[0],crossing_pedestrian_distance_range[1])
    num = random.randint(1, 3)
    for j in range(1,1+num):
        pedestrian_num += 1
        age = random.choice(ages)
        gender = random.choice(genders)
        scenario = scenario + f"    pedestrian{pedestrian_num} = pedestrian(age='{age}', gender='{gender}', offset=-3.5, distance={crossing_pedestrian_distance + j - 1}, initial_speed=4, direction=1) \n"
    roadside_pedestrian_distance = random.uniform(roadside_pedestrian_distance_range[0],roadside_pedestrian_distance_range[1])
    num = random.randint(0,3)
    for j in range(1, 1+num):
        pedestrian_num += 1
        age = random.choice(ages)
        gender = random.choice(genders)
        scenario = scenario + f"    pedestrian{pedestrian_num} = pedestrian(age='{age}', gender='{gender}', offset=-3.5, distance={roadside_pedestrian_distance + j - 1}, initial_speed=4, direction=0) \n"

    all_results.append(scenario)
    print(scenario)

df = pd.DataFrame(all_results, columns=["Logical Scenarios"])
df["Flag"] = None
# 写入 Excel
df.to_excel(result_file, index=False)
