import os

import pandas as pd
import openai
import time

api_key=""
base_url=""

output="scenario_result/functional_scenario.xlsx"

# 加载数据
seed_df = pd.read_excel("seed_scenarios.xlsx")
variables_df = pd.read_excel("variation_variables.xlsx")

# 合并所有种子场景
all_scenarios = "\n".join([f"Scenarios {i+1}: {row[0]} - {row[1]}" for i, row in seed_df.iterrows()])

# 合并所有变点变量
variables = []
for _, row in variables_df.iterrows():
    var_name = row[0]  # 变量名称
    values = [v for v in row[1:] if pd.notna(v)]  # 去除 NaN 值
    variables.append(f"{var_name}: {', '.join(values)}")
all_variables = "\n".join(variables)


# 调用 GPT-4o API
from openai import OpenAI
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 场景生成函数（分批）
def generate_batch(index, existing_scenes, batch_size=8):
    """
    每批生成 batch_size 个场景。
    """
    memory = "\n".join(existing_scenes) if existing_scenes else "无"

    prompt = (
        f"### Autonomous Driving Ethical Incident Seed Scenario Description:\n{all_scenarios}\n\n"
        f"### CARLA Variation Point Variables:\n{all_variables}\n\n"
        "### Already Generated Scenarios (to prevent duplication):\n"
        f"{memory}\n\n"
        f"### Generate New Autonomous Driving Ethical Incident Scenarios:\n"
        f"Based on the above scenarios and variation variables, generate {batch_size} new autonomous driving ethical incident scenarios. (Start counting from {index})\n"
        "Each scenario must strictly follow the format below (ensure the values for title, description, and variation variables are all on the same line), for example:\n"
        "{\n"
        '  "Title": "Scenario 1: xxx",\n'
        '  "Description": "xxx",\n'
        '  "Variation Variables": "xxx"\n'
        "}\n"
        'Make sure to use double quotes for "Title", "Description", and "Variation Variables"\n'
        "CARLA doesn't involve whether there are helmets, CARLA assumes no people in vehicles by default. Don't consider passenger conditions - treat the vehicle as a whole. All other detailed variation points can be found above.\n"
        "Strictly adhere to the value ranges specified in the variation point variables. Do not include animals or other unspecified elements. Avoid relying on previously generated scenarios when creating new ones. Additionally, consider introducing dilemmas involving vehicle-to-vehicle decisions."
        "Ensure each scenario is independent and diverse."
        '**IMPORTANT: Respond in English only.**'
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an autonomous driving ethical scenario generation expert."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4096
    )
    return response.choices[0].message.content


# 生成新场景
print("Generating new autonomous driving accident scenarios...")

batch_size = 10  # 每次生成 n 个场景
total_scenes = 200  # 目标总数
scene_list = []
existing_scenes = []

for i in range(0, total_scenes, batch_size):
    print(f"Generating scenarios {i+1} to {i + batch_size} ...")

    for attempt in range(10): # 最大试10次
        try:
            # 分批生成
            scene_text = generate_batch(i+1,existing_scenes, batch_size)
            if scene_text:
                print(scene_text)
                scenes = scene_text.split("\n")
                title = ""
                description = ""
                variables = ""
                flag = 0
                for scene in scenes: # 切割输出的结果
                    if "\"Title\"" in scene:
                        flag += 1
                        title = scene
                        existing_scenes.append(scene)
                    if "\"Description\"" in scene:
                        flag += 1
                        description = scene
                        existing_scenes.append(scene)
                    if "\"Variation Variables\"" in scene:
                        flag += 1
                        variables = scene
                        existing_scenes.append(scene)
                    if flag == 3:
                        scene_list.append({
                            "Title": title,
                            "Description": description,
                            "Variation Variables": variables,
                            "Flag": None
                        })
                        title = ""
                        description = ""
                        variables = ""
                        flag = 0
                #  每次生成后保存（追加模式）
                if os.path.exists(output):
                    old_df = pd.read_excel(output)
                    combined_df = pd.concat([old_df, pd.DataFrame(scene_list)], ignore_index=True)
                    combined_df.to_excel(output, index=False)
                else:
                    pd.DataFrame(scene_list).to_excel(output, index=False)

                scene_list = []  # 清空临时列表，避免重复写入
                break
            else:
                print("Scenario generation failed. Please check the error message.")
            # 防止速率限制，稍作延迟
        except Exception as e:
            print(f"Attempt {attempt + 1}/10 failed: {e}")
            if attempt < 10:
                time.sleep(4)
            else:
                print("Maximum retry attempts reached. Saving generated results and exiting.")
                exit()
    time.sleep(5)