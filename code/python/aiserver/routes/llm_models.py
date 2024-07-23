from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Union
from llms.llm_manager import LLMManager

llm_models_router = APIRouter()


@llm_models_router.get('/llm-models')
async def get_llm_models(provider: str = Query('', description="LLM provider name")):
    try:
        models = LLMManager.fetch_models(provider.lower())
        return {"models": models}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models for provider {provider}: {str(e)}")


@llm_models_router.get('/llm-providers', response_model=Dict[str, List[Dict[str, Union[str, List[str]]]]])
async def get_llm_providers():
    try:
        providers_data = []
        for provider_name, provider in LLMManager.providers.items():
            models = provider.fetch_models()
            default_model = provider.get_default_model()

            # Ensure the default model is the first in the list
            if default_model in models:
                models.remove(default_model)
            models.insert(0, default_model)

            providers_data.append({
                "provider": provider_name,
                "models": models
            })

        return {"providers": providers_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch LLM providers and models: {str(e)}")