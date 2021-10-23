#!/bin/bash

# Run the RiskDriver.py script using python3.
# Detach it from the terminal using nohup.
# Forward stdout to null because it is not necessary to log the output.
# Forward stderr to stdout, which will itself be forwarded to nohup.out.
#	because we do want to log error messages in the event of a crash.
# Lastly, place a & at the end so this task runs in the background.

nohup python3 RiskDriver.py > ./Outputs/Output.txt 2> ./Outputs/Error.txt &
