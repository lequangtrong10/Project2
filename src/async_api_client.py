import asyncio
import aiohttp


API_URL = "https://api.tiki.vn/product-detail/api/v1/products/{id}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://tiki.vn/",
    "Origin": "https://tiki.vn",
}

async def fetch_product_async(session, product_id, timeout=10):
    """
    Gọi API Tiki bất đồng bộ cho 1 product_id.
    """
    url = API_URL.format(id=product_id)

    try:
        async with session.get(url, headers=HEADERS, timeout=timeout) as response:
            status_code = response.status

            if status_code != 200:
                return {
                    "id": product_id,
                    "success": False,
                    "status_code": status_code,
                    "data": None,
                    "error": f"HTTP_ERROR_{status_code}",
                }

            data = await response.json()

            return {
                "id": product_id,
                "success": True,
                "status_code": status_code,
                "data": data,
                "error": None,
            }

    except asyncio.TimeoutError:
        return {
            "id": product_id,
            "success": False,
            "status_code": None,
            "data": None,
            "error": "TIMEOUT_ERROR",
        }

    except aiohttp.ClientError as e:
        return {
            "id": product_id,
            "success": False,
            "status_code": None,
            "data": None,
            "error": f"REQUEST_ERROR: {e}",
        }

    except Exception as e:
        return {
            "id": product_id,
            "success": False,
            "status_code": None,
            "data": None,
            "error": f"UNKNOWN_ERROR: {e}",
        }


async def fetch_many_products_async(product_ids, concurrency=50, timeout=10):
    """
    Gọi API nhiều product_id cùng lúc, có giới hạn concurrency.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession() as session:

        async def fetch_with_semaphore(product_id):
            async with semaphore:
                return await fetch_product_async(
                    session=session,
                    product_id=product_id,
                    timeout=timeout,
                )

        tasks = [
            fetch_with_semaphore(product_id)
            for product_id in product_ids
        ]

        return await asyncio.gather(*tasks)