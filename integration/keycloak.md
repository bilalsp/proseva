# KEYCLOAK

NOTE: You can also import realm instead of following all the below steps. 
Realm file: /data/internal-realm-export.json



- Create a Realm `internal`


- IAM service
    - Create a client `iam-service`
        - Name: `Identity and Access Management (IAM) Service`
        - Client authentication: `On`
        - Authentication flow: `Service accounts roles`
    - Add audience in token
        - Name: `audience-iam-service`
        - Configure a new mapper
            - Mapper type: `Audience`
            - Mapper name: `audience-iam-service`
            - Included Client Audience: `audience-iam`
            - Add to access token: `On`


- Swagger UI for IAM service
    - Create a client `iam-service-swagger-ui`
        - Name: `Swagger UI for Identity and Access Management (IAM) Service`
        - Authentication flow: `Standard flow`
        - Valid redirect URIs: /*, http://localhost/*
        - Web origins: +
    - Add client scope: `audience-iam-service` as a default
    - Navigate to Advanced Settings
        - Proof Key for Code Exchange Code Challenge Method: `S256`


- Users
    - Create new user
        - username: `user-1`
        - Credentials -> Set password
