minAttackFile = "./AttackStatistics-MinAttackers.txt"
maxAttackFile = "./AttackStatistics-MaxAttackers.txt"

with open(minAttackFile) as minfile:
    with open(maxAttackFile) as maxfile:
        eof_reached = False
        minLine = minfile.readline().strip()
        maxLine = maxfile.readline().strip()
        while(not eof_reached):
            minLineParts = minLine.split(",")
            maxLineParts = maxLine.split(",")
            minLineStats = {}
            maxLineStats = {}

            for part in minLineParts:
                pair = part.split(":")
                minLineStats[pair[0].strip()] = pair[1].strip()

            for part in maxLineParts:
                pair = part.split(":")
                maxLineStats[pair[0].strip()] = pair[1].strip()

            AtkRemAvg = float(maxLineStats["AtkRemAvg"]) - float(minLineStats["AtkRemAvg"])
            DfdRemAvg = float(maxLineStats["DfdRemAvg"]) - float(minLineStats["DfdRemAvg"])
            AtkSucAvg = float(maxLineStats["AtkSucAvg"]) - float(minLineStats["AtkSucAvg"])
            DfdSucAvg = float(maxLineStats["DfdSucAvg"]) - float(minLineStats["DfdSucAvg"])

            diffLine = f"Dif|Atk:{maxLineStats['Atk'].strip()}, dfd:{maxLineStats['dfd'].strip()}, "
            diffLine += f"AtkRemAvg:{AtkRemAvg}, DfdRemAvg:{DfdRemAvg}, AtkSucAvg:{AtkSucAvg}, DfdSucAvg:{DfdSucAvg}"
            if(abs(AtkSucAvg) > 0.50):
                diffLine = "!" + diffLine

            print("Max|" + maxLine.strip())
            print("Min|" + minLine.strip())
            print(diffLine.strip())

            minLine = minfile.readline()
            maxLine = maxfile.readline()
            if(minLine == "" or maxLine == ""):
                eof_reached = True