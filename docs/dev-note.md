# Steps required when developing mscore
- If you add new dependency in mscore, then you have to push it to github.
    and change rev of mscore whichever microservice is using it...
    mscore = { git = "https://github.com/bilalsp/proseva.git", subdirectory = "libs/mscore", rev="915e143" }
