from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from image_recognition import recognize_heroes, enums
from hero_fetching import get_resources
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="AFK Arena Hero Recognition API", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HeroRecognitionConfig(BaseModel):
    filename: str = Field(..., description="Uploaded screen name.")
    faction: enums.HeroFaction = Field(
        None,
        description="Faction of heroes to search for. By default includes all factions.",
    )
    class_name: enums.HeroClass = Field(
        None,
        description="Class of champions to search for. By default includes all classes.",
        alias="class",
    )
    include_common: bool = Field(
        False,
        description="Indicates whether it should include common heroes.",
        alias="includeCommon",
    )


class HeroRecognitionResponse(BaseModel):
    name: str
    faction: enums.HeroFaction
    class_name: enums.HeroClass = Field(..., alias="class")
    rarity: enums.HeroRarity
    ascension: enums.HeroAscension
    stars: int = None
    level: int = None


@app.post(
    "/api/v1/hero_recognition",
    response_model=List[List[HeroRecognitionResponse]],
    tags=["hero-recognition"],
)
async def hero_recognition(configs: List[HeroRecognitionConfig]):
    response = []

    for config in configs:
        response.append(
            recognize_heroes(
                config.filename,
                config.faction,
                config.class_name,
                config.include_common,
            )
        )

    return response


@app.post(
    "/api/v1/update_resources", tags=["hero-recognition"],
)
async def update_resources():
    get_resources()


# uvicorn main:app --reload
