#
# REFERENCE: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/working-with-ssh-key-passphrases
#

#!/bin/bash

# Set the location of the agent environment file
env=~/.ssh/agent.env

# Function to load the agent environment variables if they exist
agent_load_env () {
    test -f "$env" && . "$env" >| /dev/null
}

# Function to start the ssh-agent and save its environment variables
agent_start () {
    (umask 077; ssh-agent >| "$env")
    . "$env" >| /dev/null
}

# Load the agent environment if available
agent_load_env

# Determine the agent's state:
# 0 = agent running with key
# 1 = agent running without key
# 2 = agent not running
agent_run_state=$(ssh-add -l >| /dev/null 2>&1; echo $?)

# Check agent status and act accordingly
if [ ! "$SSH_AUTH_SOCK" ] || [ $agent_run_state = 2 ]; then
    # If no agent is running or agent isn't running with a key, start it
    agent_start
    ssh-add
elif [ "$SSH_AUTH_SOCK" ] && [ $agent_run_state = 1 ]; then
    # If agent is running but no key is loaded, load the key
    ssh-add
fi

# Clean up the environment file after the process
unset env
