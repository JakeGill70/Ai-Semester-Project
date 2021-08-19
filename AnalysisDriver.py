import os
from Agent import Agent
from Agent import AgentCharacteristic
from AgentReader import AgentReader
import matplotlib.pyplot as plt
import math
import tkinter as tk


def getAverageAgentFilePathNames(directoryPath):
    agentFilePathNames = []
    absDirectory = os.path.abspath(directoryPath)
    for file in os.listdir(absDirectory):
        agentFilePathNames.append(os.path.join(absDirectory, file))
    return agentFilePathNames


def getListOfAverageAgents(fileNames):
    agents = []
    for fileName in fileNames:
        agents.append(AgentReader.readAgent(fileName))
    return agents


def summaryPlots(agents):
    # Use the characteristics of whatever the first
    #   agent has to get characteristic structure info
    baseAgent = agents[0]
    x = range(len(agents))
    for characteristicCategoryName in baseAgent.characteristics.keys():
        numberOfItemsInCategory = len(baseAgent.characteristics[characteristicCategoryName].keys())
        sqrtNOIIC = math.ceil(math.sqrt(numberOfItemsInCategory))
        fig, axes = plt.subplots(nrows=sqrtNOIIC, ncols=sqrtNOIIC)
        i = 0
        j = 0
        for characteristicName in baseAgent.characteristics[characteristicCategoryName].keys():
            y = [agent.characteristics[characteristicCategoryName][characteristicName].value for agent in agents]

            axes[i][j].plot(x, y)
            axes[i][j].set_title(f"{characteristicCategoryName} - {characteristicName}")
            axes[i][j].set_xlabel("Generation")
            axes[i][j].set_ylabel("Value")
            i += 1
            if(i % sqrtNOIIC == 0):
                i = 0
                j += 1

        fig.show()


def loadAgents(agents):
    agents.clear()
    folderPath = tk.filedialog.askdirectory()
    pathNames = getAverageAgentFilePathNames(folderPath)
    for agent in getListOfAverageAgents(pathNames):
        agents.append(agent)


# print(folderPath)
# pathNames = getAverageAgentFilePathNames("./Average Agents/2021-08-18-11PM-25")
# print(pathNames)
# print("\n\n\n")
# agents = getListOfAverageAgents(pathNames)
# print([a.name for a in agents])
agents = []
root = tk.Tk()

canvas = tk.Canvas(root)
canvas.grid(rowspan=40)

# Load agents
load_btn = tk.Button(root, text="Load Agent Directory", command=lambda: loadAgents(agents))
load_btn.grid(row=0)

# Summary Button
summary_btn = tk.Button(root, text="Summary Graphs", command=lambda: summaryPlots(agents))
summary_btn.grid(row=1)

root.mainloop()
