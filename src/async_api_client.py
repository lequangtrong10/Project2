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
    Fetch product information asynchronously from the Tiki API.

    Args:
        session (aiohttp.ClientSession):
            Active HTTP session used for sending requests.

        product_id (str):
            Tiki product identifier.

        timeout (int, optional):
            Request timeout in seconds. Defaults to 10.

    Returns:
        dict:
            Dictionary containing request status, response data,
            HTTP status code, and error information.

    Raises:
        No exception is propagated. All exceptions are converted
        into structured error responses.
    """
    url = API_URL.format(id=product_id)

    try:
        async with session.get(
            url,
            headers=HEADERS,
            timeout=timeout,
        ) as response:

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

    except aiohttp.ClientError as error:
        return {
            "id": product_id,
            "success": False,
            "status_code": None,
            "data": None,
            "error": f"REQUEST_ERROR: {error}",
        }

    except Exception as error:
        return {
            "id": product_id,
            "success": False,
            "status_code": None,
            "data": None,
            "error": f"UNKNOWN_ERROR: {error}",
        }


async def fetch_many_products_async(
    product_ids,
    concurrency=50,
    timeout=10,
):
    """
    Fetch multiple products concurrently using asyncio.

    Args:
        product_ids (list[str]):
            List of Tiki product IDs.

        concurrency (int, optional):
            Maximum number of simultaneous requests.
            Defaults to 50.

        timeout (int, optional):
            Request timeout in seconds.
            Defaults to 10.

    Returns:
        list[dict]:
            List of API responses for all requested products.
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