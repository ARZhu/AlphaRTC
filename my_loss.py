import argparse
import json
import seaborn as sns
import matplotlib.pyplot as plt


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# 使用命令行参数-i指定输入文件名

import argparse
import json
import re
# 使用命令行参数-i指定输入文件名



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt

input_path = './test_data/webrtc.log'
loss_list = []
payload_percent_list = []

with open(input_path, mode="r", encoding="utf-8-sig") as f:
    # out_file = open(args.input[:-4] + "_loss.out", "w+")

    flag = False
    last_arrival_time = 0
    total_time_ms = 0
    total_loss = 0
    total_count = 0

    count_dealed = False
    loss_dealed = False

    max_size = 0
    
    while(True):
        text_line = f.readline()
        if(text_line):
            
            if text_line.startswith("(video_send_stream_impl.cc:231): VideoSendStreamInternal:"):
                print(text_line[len('(video_send_stream_impl.cc:231): VideoSendStreamInternal:'):])
                index_start = text_line.find("max_packet_size:") + len("max_packet_size:")
                print(index_start)
                # get the number by re
                print(text_line[index_start:index_start + 5])
                max_size = re.findall(r"\d+", text_line[index_start:index_start + 10])
                max_size = int(max_size[0])
            
            if(text_line.startswith("(remote_estimator_proxy.cc:151):")):
                json_data = json.loads(text_line[33:])
                arrivalTimeMs = int(json_data["packetInfo"]["arrivalTimeMs"])
                # print(arrivalTimeMs)
                payloadSize = json_data["packetInfo"]["payloadSize"]

                if(flag == False):
                    flag = True
                #    last_arrival_time = arrivalTimeMs

                # 过了1s时间，输出吞吐量
                # if(total_time_ms + arrivalTimeMs - last_arrival_time > 200):
                #     print(total_loss / total_count, file=out_file)
                #     total_time_ms = 0
                #     # total_payload_size = 0
                #     total_loss = 0
                #     total_count = 0

                # total_payload_size += int(payloadSize)
                # total_time_ms += arrivalTimeMs - last_arrival_time
                # last_arrival_time = arrivalTimeMs
                count_dealed = False
                loss_dealed = False
                if total_count == 0:
                    loss_list.append((arrivalTimeMs, 0))
                else:
                    loss_list.append((arrivalTimeMs, total_loss / total_count))
                
                payload_percent_list.append((arrivalTimeMs, (max_size - int(payloadSize)) / max_size))
            
            if(text_line.startswith("(receive_statistics_impl.cc:210):") and not count_dealed):
                total_count += 1
                count_dealed = True
            
            if(text_line.startswith("(receive_statistics_impl.cc:267):") and not loss_dealed):
                total_loss += (int)(text_line.strip()[-1])
                loss_dealed = True
            
            #print(arrivalTimeMs, payloadSize, file=out_file)
        else:
            break
    #print(total_payload_size, total_time)
    print(total_loss / total_count if total_count != 0 else 0)
    f.close()
    #out_file.close()

loss_list = np.array(loss_list)
loss_list = pd.DataFrame(loss_list, columns=["arrival_time_ms", "loss"])
print(loss_list["arrival_time_ms"])
# for i in range(1, len(loss_list['arrival_time_ms'])):
#     loss_list['arrival_time_ms'][i] = loss_list['arrival_time_ms'][i] - loss_list['arrival_time_ms'][0]

first_arrival_time = loss_list['arrival_time_ms'][0]
loss_list['arrival_time_ms'] = loss_list['arrival_time_ms'] - first_arrival_time
print(loss_list["arrival_time_ms"])

fig = plt.figure()

ax = fig.gca()

# ax.plot(loss_list["arrival_time_ms"], loss_list["loss"])
sns.lineplot(data=loss_list, x="arrival_time_ms", y="loss")
ax.set_ylim(-0.5, 1.05)
ax.set_xlabel("time (ms)")
ax.set_ylabel("loss")
ax.set_title(f"loss: {total_loss / total_count if total_count != 0 else 0}")

fig.savefig("loss.png")

payload_percent_list = np.array(payload_percent_list)
payload_percent_list = pd.DataFrame(payload_percent_list, columns=["arrival_time_ms", "payload_percent"])
print(payload_percent_list["arrival_time_ms"])
first_arrival_time = payload_percent_list['arrival_time_ms'][0]
payload_percent_list['arrival_time_ms'] = payload_percent_list['arrival_time_ms'] - first_arrival_time
print(payload_percent_list["arrival_time_ms"])

print(payload_percent_list)

fig = plt.figure()


ax = fig.gca()

# ax.plot(loss_list["arrival_time_ms"], loss_list["loss"])
sns.lineplot(data=payload_percent_list, x="arrival_time_ms", y="payload_percent")
ax.set_ylim(-0.1, 1.05)
ax.set_xlabel("time (ms)")
ax.set_ylabel("loss_percent")
ax.set_title(f"loss_percent: {np.mean(payload_percent_list['payload_percent'])}")

fig.savefig("loss_percent.png")