# sys-integration

# Write to README one for user and another for developer


## 1. SSH
- Clone this repository inside following directory
    `C:\Program Files\Git\opt`

- If your ssh key is protected by passphrase then run following command from `Git Bash` shell
    
    ```bash
    cp ~/opt/proseva/integration/scripts/start-ssh-agent.sh ~/
    echo "source ~/start-ssh-agent.sh" >> ~/.bashrc
    source ~/.bashrc # (To apply the changes, you can either restart the terminal or run it)
    ```

## 2. Generate PAT (Personal Access Token)
It is required to install the dependency (`mscore`) from private repository.
- Visit: `https://github.com/settings/personal-access-tokens/new`
- Repository access: `bilalsp/proseva`
- Repository permissions -> Contents -> Access: `Read-only`
- Generate Token
- Set the generated token in `/proseva/.env` file


## 3. Generate certificate
```sh 
bash scripts/certificate/gen-self-signed-certs.bash
```

## 4. DNS
```sh
# run below command using administrator privilege
bash scripts/add_hosts_entries.sh
```





<!-- - Some usefull commands of SSH

    [1] Test your SSH connection to GitHub:
    `ssh -T git@github.com`

    [2] List the SSH keys currently loaded into your SSH agent:
    `ssh-add -l`

    [3] To remove all SSH keys currently loaded into your SSH agent:
    `ssh-add -D`

    [4] To change or remove the passphrase of an existing SSH private key:
    `ssh-keygen -p` -->
