# Roadmap

## Proper project documentation
Taglines:
- "ProSeva – India's Trusted Professionals Service Hub"
- "ProSeva: Where Professionals Meet Purpose."
- "Seva with Skill, Delivered with Trust."

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

## [-] mscore
- document proper status code return by each endpoint in swagger using responses in FastAPI
- other functionalites: vault support, backend-for-frontend

## [-] miscorservice
- unittests
- end2end tests (postman)

## [-] low priority
- revisit docker-compose.yml: setup proper configuration for reverse-proxy
    - docker compose up --watch
      Ref. https://docs.docker.com/compose/how-tos/file-watch/
- add vault service to store secrets
- generate proper self signed certificate


## [-] high priority
  - fix type: lisiting to listing





## mscore

- keywords for future dev: 
    - raise_error_from_response, raise_error_for_status
    - MSCoreUserError similar to PydanticUserError 



- Project Structure
    - https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/ (src layout vs flat layout)
    - https://chat.openai.com/c/cde7a8b3-0c35-489e-891c-d61d2ebcce8e

- Pre-commit
    - https://github.com/alessandrojcm/commitlint-pre-commit-hook

- lifespan discussion
    - https://github.com/tiangolo/fastapi/discussions/9397
    - https://github.com/tiangolo/fastapi/discussions/10083

- keycloak 
    - https://www.youtube.com/watch?v=G2QVhUAEylc
    - https://stackoverflow.com/questions/65782574/keycloak-include-the-roles-of-requested-scopes-in-generated-tokens
    - https://github.com/surfer190/fixes/tree/master/docs/keycloak
    - https://www.keycloak.org/docs-api/21.0.1/rest-api/index.html
    - https://github.com/surfer190/fixes/tree/master/docs/keycloak
    - https://github.com/flavien-hugs/keycloak-auth-microservice/tree/main
    
- fastapi:
    - https://fastapi-utils.davidmontague.xyz/
    - https://fastapi-utils.davidmontague.xyz/user-guide/basics/api-model/
    - https://fastapitutorial.com/
    - https://github.com/mozilla-it/ctms-api/tree/main [Project]
    - https://github.com/identixone/fastapi_contrib
    - https://github.com/fastapi-users/fastapi-users
    - https://github.com/MushroomMaula/fastapi_login
    - https://github.com/holgi/fastapi-permissions

    [Less Important]
    - https://github.com/ManiMozaffar/fast-student/tree/main
    - https://github.com/pycasbin/fastapi-authz

- fastapi based projects
    - https://github.com/Netflix/dispatch

- pydantic:
    - https://docs.pydantic.dev/latest/concepts/pydantic_settings

- typing
    - https://github.com/uriyyo/fastapi-lifespan-manager/blob/main/fastapi_lifespan_manager/types.py

- Kill running process on windows using PORT
    - https://stackoverflow.com/questions/39632667/how-do-i-remove-the-process-currently-using-a-port-on-localhost-in-windows

- pdm
    https://pypi.org/project/pdm/


Issues:
- Module: \mscore\mscore\lifespan\keycloak.py
    <!-- # ERROR will be raised if keycloak server is down
    #
    # keycloak.exceptions.KeycloakConnectionError: Can't connect to server (HTTPConnectionPool(host='localhost', port=8080):
    # Max retries exceeded with url: /realms/outh2-demo (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002D855F998D0>:
    # Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))) -->
