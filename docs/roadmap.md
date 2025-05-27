# Roadmap

## [-] Redirect docker logs to syslog running on host-machine
- Use Docker's --log-driver=syslog to redirect stdout/stderr to the host’s syslog. 
Logs will appear in the system logs on the host: `tail -f /var/log/syslog`  # Debian/Ubuntu

Refrences:
- https://docs.docker.com/engine/logging/drivers/syslog/
- https://stackoverflow.com/questions/43889481/docker-how-to-use-syslog-to-record-logs-on-host-machine

Sample:
```yml
    logging:
      driver: syslog
      options:
        syslog-address: "udp://rsyslog:514"
        syslog-tag: "container_name/{{.Name}}"
    depends_on:
      - rsyslog

  # setup rsyslog service if host is window machine  
  rsyslog:
    image: rsyslog/rsyslog
    container_name: rsyslog_server
    ports:
      - "514:514/udp"
    volumes:
      - ./rsyslog/rsyslog.conf:/etc/rsyslog.conf
      - rsyslog_data:/var/log      
```
