import os
from Agent import Agent
from Agent import AgentCharacteristic
from AgentReader import AgentReader
import matplotlib.pyplot as plt
import math
import tkinter as tk
from Logger import Logger, MessageTypes


def getAverageAgentFilePathNames(directoryPath):
    agentFilePathNames = []
    absDirectory = os.path.abspath(directoryPath)
    for file in os.listdir(absDirectory):
        if(file != "turnCount.txt"):
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
        fig, axes = plt.subplots(nrows=sqrtNOIIC, ncols=sqrtNOIIC, constrained_layout=True)
        fig.suptitle(characteristicCategoryName)
        fig.canvas.set_window_title(characteristicCategoryName)
        i = 0
        j = 0
        for characteristicName in baseAgent.characteristics[characteristicCategoryName].keys():
            y = [agent.characteristics[characteristicCategoryName][characteristicName].value for agent in agents]

            axes[i][j].plot(x, y)
            axes[i][j].set_title(characteristicName)
            axes[i][j].set_xlabel("Generation")
            axes[i][j].set_ylabel("Value")
            i += 1
            if(i % sqrtNOIIC == 0):
                i = 0
                j += 1

        # fig.tight_layout()
        fig.show()


def detailedPlot(agents, categoryName, characteristicName):
    # Use the characteristics of whatever the first
    #   agent has to get characteristic structure info
    baseAgent = agents[0]
    x = range(len(agents))
    y = [agent.characteristics[categoryName][characteristicName].value for agent in agents]
    plt.title(categoryName + " - " + characteristicName)
    plt.xlabel("Generation")
    plt.ylabel("Value")
    plt.plot(x, y)
    plt.show()


def loadAgents():
    agents = []
    agents.clear()
    folderPath = tk.filedialog.askdirectory()
    pathNames = getAverageAgentFilePathNames(folderPath)
    for agent in getListOfAverageAgents(pathNames):
        agents.append(agent)
    return agents


agents = loadAgents()
baseAgent = agents[0]

root = tk.Tk()

canvas = tk.Canvas(root)
canvas.grid(rowspan=40, columnspan=4)

# Load agents
load_btn = tk.Button(root, text="Load Agent Directory", command=lambda: loadAgents(agents))
load_btn.grid(row=0, column=1)

# Summary Button
summary_btn = tk.Button(root, text="Summary Graphs", command=lambda: summaryPlots(agents))
summary_btn.grid(row=1, column=1)

# Characteristics buttons
buttons = []
gridRowCount = 2
gridColumnCount = -1
for characteristicCategoryName in baseAgent.characteristics.keys():
    gridRowCount = 2

    categoryLabel = tk.Label(root, text=characteristicCategoryName)
    gridColumnCount += 1
    categoryLabel.grid(row=gridRowCount, column=gridColumnCount)
    gridRowCount += 1

    for characteristicName in baseAgent.characteristics[characteristicCategoryName].keys():
        catName = characteristicCategoryName
        charName = characteristicName
        buttons.append(tk.Button(root, text=characteristicName, command=lambda catName=catName,
                                 charName=charName: detailedPlot(agents, catName, charName)))
        Logger.message(MessageTypes.GuiBuild, f"Button for {catName} - {charName}")
        buttons[-1].grid(row=gridRowCount, column=gridColumnCount)
        gridRowCount += 1

root.mainloop()

# TODO: Add trendlines for plots
