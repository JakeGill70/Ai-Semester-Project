class AgentCharacteristic:
    def __init__(self, value, description):
        self.value = value
        self.description = description

    def __int__(self):
        return self.value


class Agent:
    def __init__(self, name):
        self.name = name
        self.characteristics = {
            "Placement": {
                "Anywhere": AgentCharacteristic(3, "Placing a unit anywhere"),
                "Enemy Adjacent": AgentCharacteristic(5, "Placing a unit on a country connected to a country controlled by a different player"),
                "Border Adjacent": AgentCharacteristic(8, "Placing a unit in a country that borders a country in a different continent"),
                "Connection Bias": AgentCharacteristic(1, "Placing a unit on a country with connections to multiple other countries, +value per connection"),
                "Placement Bias Multiplier": AgentCharacteristic(0.5, "Placing a unit where there already are other units, *value per army")
            },
            "Preference": {
                "Larger": AgentCharacteristic(1, "Preference to attack larger players"),
                "Smaller": AgentCharacteristic(1, "Preference to attack smaller players"),
                "Aggression": AgentCharacteristic(1, "Preferrence for aggressive actions"),
                "Risky": AgentCharacteristic(1, "Preference for risky actions"),
                "Safe": AgentCharacteristic(1, "Preference for safe actions")
            }
        }
