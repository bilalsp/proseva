# KEYCLOAK

NOTE: You can also import realm instead of following all the below steps. 
Realm file: /examples/data/realm-export-mscore.json


- Create a Realm `mscore`

- Create a client `api-test`
    - set authentication flow: `Direct access grants`
- Add audience in token
    - Navigate to: Clients -> `api-test` -> Client scopes -> `api-test-dedicated` -> Add mapper -> By configuration > Audience
    - Configure audience mapper
        - Mapper name: `audience-api-test`
        - Included Client Audience: `api-test`
        - Add to access token: On
- Create user attribute
    - Navigate to: Realm settings -> User profile -> Create attribute
    - Attribute name: `disabled`
    - Navigate to: Clients -> `api-test` -> Client scopes -> `api-test-dedicated` -> Add mapper -> By configuration > User Attribute
    - Configure User Attribute mapper
        - Name: user-attribute-disabled
        - User Attribute: disabled
        - Token Claim Name: disabled
        - Claim JSON Type: boolean
        - Add to access token: On
- Create roles
    - Navigate to: Clients -> `api-test` -> Roles -> Create role -> `r_me`
    - Similarly, create another `r_items` role
- Create client scopes
    - Navigate to: Client scopes
    - Client scope name: `me`
    - Include in token scope: On
    - Scope -> Assign role -> Filter by clients -> select `r_me` role
    - Navigate to: Clients -> `api-test` -> Client scopes -> Add client scope -> select `me` scope -> Add as optional
    - Similarly, create another `items` scope and assign it to `r_items`

- Create two users
    - Create a `user-1`
        - username: `user-1`
        - Action -> Impersonate
        - Credentials -> Set password
        - Role mapping -> Assign role -> Filter by clients -> select `r_me` and `r_items` roles
    - Similarly, create a `user-2` and assign only `r_me` role




