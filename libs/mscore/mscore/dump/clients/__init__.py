# class APIManager: or APIClientManager or ClientManager
#    pass
# https://github.com/microsoft/pylance-release/issues/1870

#
# httpx with client-credential support (keycloak auth)
#
# https://github.com/Colin-b/httpx_auth/tree/develop


#
# [C] 68149a99-2360-800b-b96c-1819db353fc2
# # How to reauthenticate httpx.AsyncClient if token get expired

# import httpx
# from httpx import Request
# from typing import Optional


# class KeycloakAuth(httpx.Auth):
#     requires_response_body = True

#     def __init__(
#         self,
#         server_url: str,
#         realm: str,
#         client_id: str,
#         username: str,
#         password: str,
#         client_secret: Optional[str] = None,
#     ):
#         self.token_url = f"{server_url}/realms/{realm}/protocol/openid-connect/token"
#         self.client_id = client_id
#         self.client_secret = client_secret
#         self.username = username
#         self.password = password

#         self.access_token: Optional[str] = None
#         self.refresh_token: Optional[str] = None
#         self.token_type: Optional[str] = None

#         self.token_client = httpx.AsyncClient()

#     async def login(self):
#         data = {
#             "grant_type": "password",
#             "client_id": self.client_id,
#             "username": self.username,
#             "password": self.password,
#         }
#         if self.client_secret:
#             data["client_secret"] = self.client_secret

#         response = await self.token_client.post(self.token_url, data=data)
#         response.raise_for_status()
#         tokens = response.json()
#         self._update_tokens(tokens)

#     async def refresh(self):
#         data = {
#             "grant_type": "refresh_token",
#             "client_id": self.client_id,
#             "refresh_token": self.refresh_token,
#         }
#         if self.client_secret:
#             data["client_secret"] = self.client_secret

#         response = await self.token_client.post(self.token_url, data=data)
#         response.raise_for_status()
#         tokens = response.json()
#         self._update_tokens(tokens)

#     def _update_tokens(self, tokens: dict):
#         self.access_token = tokens["access_token"]
#         self.refresh_token = tokens.get("refresh_token")
#         self.token_type = tokens.get("token_type", "Bearer")

#     async def auth_flow(self, request: Request):
#         if self.access_token is None:
#             await self.login()

#         request.headers["Authorization"] = f"{self.token_type} {self.access_token}"
#         response = yield request

#         if response.status_code == 401:
#             await self.refresh()
#             request.headers["Authorization"] = f"{self.token_type} {self.access_token}"
#             yield request

#     async def aclose(self):
#         await self.token_client.aclose()


# async def main():
#     auth = KeycloakAuth(
#         server_url="https://keycloak.example.com",
#         realm="myrealm",
#         client_id="my-client",
#         username="alice",
#         password="s3cret",
#         client_secret="optional-client-secret",  # if your client is confidential
#     )

#     async with httpx.AsyncClient(auth=auth, base_url="https://api.example.com") as client:
#         response = await client.get("/protected/resource")
#         print(response.json())

#     await auth.aclose()
