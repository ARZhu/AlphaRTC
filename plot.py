import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

with open('output.json', 'r') as f:
    data = json.load(f)

# print(data)


matrix = np.zeros((len(data['frames']), len(data['frames'][0]['metrics'])))
# print(matrix.shape)

# print(data['frames'][0])

for frame in data['frames']:
    index = frame['frameNum']
    for col, metric in enumerate(frame['metrics'].values()):
        matrix[index, col] = metric

# print(matrix)


df = pd.DataFrame(matrix, columns=data['frames'][0]['metrics'].keys())

fig = plt.figure(figsize=(10, 10))
ax = fig.gca()
sns.lineplot(data=df, dashes=False, ax = ax)
ax.set_title('Metrics over time')
ax.set_xlabel('Frame number')
ax.set_ylabel('Metric value')

fig_vmaf = plt.figure(figsize=(10, 10))
ax_vmaf = fig_vmaf.gca()

sns.lineplot(data=df['vmaf'], dashes=False, ax=ax_vmaf)
ax_vmaf.set_title('VMAF')
ax_vmaf.set_xlabel('Frame')
ax_vmaf.set_ylabel('VMAF Score')

fig.savefig('metrics.png')
fig_vmaf.savefig('vmaf.png')