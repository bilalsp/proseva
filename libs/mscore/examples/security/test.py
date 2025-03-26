from fastapi import Depends, FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer

# import httpx

app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": "api-test-swagger-ui",
        "usePkceWithAuthorizationCodeGrant": True,
    },
    # swagger_ui_oauth2_redirect_url = "/q/swagger-ui/oauth2-redirect.html",
)

# # Keycloak settings
# KEYCLOAK_SERVER = "http://localhost:8080"
# REALM = "your-realm"
# CLIENT_ID = "swagger-ui-client"
# AUTHORIZATION_URL = f"{KEYCLOAK_SERVER}/realms/{REALM}/protocol/openid-connect/auth"
# TOKEN_URL = f"{KEYCLOAK_SERVER}/realms/{REALM}/protocol/openid-connect/token"

AUTHORIZATION_URL = "http://localhost:8080/realms/mscore/protocol/openid-connect/auth"
TOKEN_URL = "http://localhost:8080/realms/mscore/protocol/openid-connect/token"


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=AUTHORIZATION_URL, tokenUrl=TOKEN_URL
)

# # Update the OpenAPI schema to use OAuth2
# app.openapi_schema["components"]["securitySchemes"] = {
#     "OAuth2AuthorizationCodeBearer": SecurityScheme(
#         type="oauth2",
#         flows=OAuthFlowsModel(
#             authorizationCode=OAuthFlowAuthorizationCode(
#                 authorizationUrl=AUTHORIZATION_URL,
#                 tokenUrl=TOKEN_URL
#             )
#         )
#     ).dict()
# }
# app.openapi_schema["security"] = [{"OAuth2AuthorizationCodeBearer": []}]


async def verify_token(token: str = Depends(oauth2_scheme)):
    return token
    # # Token verification logic here, possibly using Keycloak introspection
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         TOKEN_URL,
    #         data={"token": token, "client_id": CLIENT_ID}
    #     )
    #     if response.status_code != 200:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Invalid token"
    #         )
    #     token_data = response.json()
    #     if not token_data.get("active"):
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Token is not active"
    #         )
    #     return token_data


@app.get("/protected-endpoint")
async def protected_endpoint(token_data: dict = Depends(verify_token)):
    return {"message": "Hello from Microservice-2!", "token_data": token_data}


# Run the FastAPI server with uvicorn
