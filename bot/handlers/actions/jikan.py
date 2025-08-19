import aiohttp

async def search_anime_jikan(title_en: str):
    url = f"https://api.jikan.moe/v4/anime?q={title_en}&limit=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data.get("data", [])