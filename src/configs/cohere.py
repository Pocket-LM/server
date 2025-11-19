from cohere import ClientV2

from src.configs.settings import settings

cohere_ranker = ClientV2(api_key=settings.COHERE_API_KEY)
