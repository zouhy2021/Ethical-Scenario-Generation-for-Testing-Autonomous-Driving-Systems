import os

import pandas as pd
import time
import yaml
from openai import OpenAI

api_key=""
base_url=""

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

para_file = "parameter_mmfn.yaml"
variables_df = pd.read_excel("variation_variables.xlsx")
output = "scenario_result/logical_scenario_mmfn.xlsx"
input = "scenario_result/functional_scenario.xlsx"

# Define the role prompt
role_prompt = ("You are an expert in Simulation-based Testing for Autonomous Driving Systems, "
                "with the goal of generating logical scenarios with suitable parameter "
                "that correspond to dilemma scenario descriptions. ")

intro_gen_scenario = "Here is the ego vehicle, vehicle model, cyclist_model, pedestrian model and the scenario model: "

ego_vehicle = (   "class ego_vehicle: \n"
                  "    def __init__(self, lane_id: int, initial_speed: float, direction: int): \n"
                  "        pass\n")

vehicle_model = ("class vehicle: \n"
                  "    def __init__(self, lane_id: int, distance: float, initial_speed: float, direction: int): \n"
                  "        pass\n")

cyclist_model = ("class cyclist: \n"
                  "    def __init__(self, lane_id: int, distance: float, initial_speed: float, direction: int): \n"
                  "        pass\n")

pedestrian_model = ("class pedestrian: \n"
                  "    def __init__(self, age: string, gender: string, offset: float, distance: float, initial_speed: float, direction: int): \n"
                  "        pass\n")

scenario_example = (     "def scenario(): \n"
                         "    road_type = \"Straight Road\"\n"
                         "    environment = \"rainy\"\n"
                         "    ego_vehicle = vehicle(lane_id=1 , initial_speed=7 , direction=1) \n"
                         "    vehicle1 = vehicle(lane_id= , distance= , initial_speed= , direction= ) \n"
                         "    cyclist1 = cyclist(lane_id= , distance= , initial_speed= , direction= ) \n"
                         "    pedestrian1 = pedestrian(age='', gender='', offset= ,distance= , initial_speed= , direction= ) \n"
                         )
try:
    with open(rf'config/{para_file}', 'r', encoding='utf-8') as file:
        parameter_string = file.read()
    with open(f"config/{para_file}", "r") as f:
        params = yaml.safe_load(f)
except FileNotFoundError:
    print(f"error: {para_file} not found")
except Exception as e:
    print(f"error: {e}")

parameter = (f"{para_file}:corresponding parameter value:\n"
             f"{parameter_string}\n")

attention_gen_scenario = ("Attention: \n"
                          "1. just output the new scenario in a code snippet with the format of the example scenario model, "
                          "which only contain the class initialization;\n"
                          "2. each vehicle object is named as 'vehicle{1-n}'(or pedestrian/cyclist)\n"
                          "3. strictly adhere to the variable values in the scene description for road types and environments\n"
                          "4. The final output result starts with def and follows the same format as the template, without any unnecessary content\n"
                          "5. Please pay attention when filling in parameters:The parameters of ego_vehicle are fixed. The distances of adjacent NPC vehicles(or cyclist) are always 5 farther away from 0, and the distance between pedestrians is 1; Do not have two actors with the same distance on the same lane ID.\n"
                          "6. The direction value of the vehicle (or cyclist) class is 1, which represents the same direction as the ego vehicle, and -1 represents the opposite direction of the vehicle;\n"
                          "7. The direction value of the pedestrian class is 1, which represents crossing the road, and 0, which represents walking on the roadside;\n"
                          f"8. When there are no vehicles behind in the same lane, the pedestrian crossing distance is {params['dangerous_crossing_pedestrian_distance']}; otherwise, it is {params['safe_crossing_pedestrian_distance']} as specified in {para_file};\n"
                          "9. The generated scene fixes the ego vehicle in the farthest right lane 1, with the sidewalk to its right and lane 2 to its left. Left-adjacent vehicles are in lane 2 (including parked vehicle).\n"
                          "10. The initial speed of the parked vehicle is 0 and the lane id of parked vehicle is 0.\n"
                         )


input_excel = input
df = pd.read_excel(input_excel, header=0)
for index, row in df.iterrows():
    if row['Flag'] == 1 or pd.isna(row['Description']):
        continue
    description_string = row['Description']
    variation_variables_string = row['Variation Variables']
    print(f"第 {index + 1} 行:")
    # print(f"  Description: {description_string}")
    # print(f"  Variation Variables: {variation_variables_string}")

    scene = f"{description_string} {variation_variables_string} ignore the parameter values given in Variation Variables (if any)"


    user_prompt = f"{intro_gen_scenario}\n{ego_vehicle}\n{vehicle_model}\n{cyclist_model}\n{pedestrian_model}\n{scenario_example}\nNow the input scene is:\n{scene}\nthe parameter config is:\n{parameter}\n{attention_gen_scenario}"

    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": role_prompt},
                      {"role": "user", "content": user_prompt}],
            temperature=0.7,
            max_tokens=4096
    )
    res = response.choices[0].message.content
    print(res)
    if pd.isna(row['Flag']):
        df.at[index, 'Flag'] = 1
    # if pd.isna(row['Result']):
    #     df.at[index, 'Result'] = response.choices[0].message.content
    df.to_excel(input, index=False)
    result_file = output
    result_df = pd.DataFrame({
        "Logical Scenarios": [res],
        "Flag": ""
    })

    if os.path.exists(result_file):
        with pd.ExcelWriter(result_file, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
            # 读取已有数据
            df_old = pd.read_excel(result_file)
            # 合并
            df_all = pd.concat([df_old, result_df], ignore_index=True)
            # 覆盖写回同一个 sheet
            df_all.to_excel(writer, index=False, sheet_name="Sheet1")
    else:
        result_df.to_excel(result_file, index=False)


    print("-" * 30)  # 分隔线