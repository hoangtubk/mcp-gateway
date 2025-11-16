# server.py
from mcp.server.fastmcp import FastMCP
import sys
import logging
import requests

logger = logging.getLogger('Calculator')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

import math
import random

# Create an MCP server
mcp = FastMCP("lxdata")

# Add an addition tool
@mcp.tool()
def calculator(python_expression: str) -> dict:
    """For mathamatical calculation, always use this tool to calculate the result of a python expression. You can use 'math' or 'random' directly, without 'import'."""
    result = eval(python_expression, {"math": math, "random": random})
    logger.info(f"Calculating formula: {python_expression}, result: {result}")
    return {"success": True, "result": result}    
    
# Add an addition tool
@mcp.tool()
def weather(location: str, date: str) -> dict:
    """Bất kỳ khi nào được hỏi về thời tiết thì hãy đọc lại kết quả bằng cách gọi API, lưu ý đọc rõ nhiệt độ kèm theo tình trạng thời tiết hiện tại. kèm theo một câu đùa vui về thời tiết."""
    api_url = f"https://api.lxdata.vn/mcpcore/v1/get_weather?location={location}&date={date}"

    try:
        resp = requests.get(api_url, timeout=5)
        resp.raise_for_status()
        # Parse JSON response
        result = resp.json()
        logger.info(f"weather: result: {result}")
        logger.info(f"location: {location}, date: {date}")
        return {"success": True, "result": result}
    except requests.RequestException as e:
        logger.error(f"Failed to fetch weather from {api_url}: {e}")
        return {"success": False, "error": str(e)}

# Add an addition tool
@mcp.tool()
def lottery(region:str = "mien-bac-xsmb", date: str = None) -> dict:
    
    """Bất cứ khi nào được hỏi về xổ số thì đọc kết quả bằng cách gọi API. 
    Lưu ý: input gồm 2 tham số: region (mặc định là 'mien-bac-xsmb') và date (mặc định là ngày hiện tại).
    region: có thể là xổ số miền nam (mien-nam-xsmn), xổ số miền trung (mien-trung-xsmt), xổ số miền bắc (mien-bac-xsmb)
    date: định dạng 'YYYY-MM-DD', ví dụ: '2023-10-01'
    1. chỉ đọc giải đặc biệt (ĐB) nếu không được yêu cầu đọc đầy đủ tất cả. 
    2. Đọc lần lượt từng chữ số
    Hỏi thêm bạn có muốn mình dự đoán kết quả xổ số ngày mai không? nếu câu trả lời là có thì đưa ra câu trả lời bằng cách gọi tool guess_lottery"""
    api_url = f"https://api.lxdata.vn/mcpcore/v1/get_lottery?region={region}&date={date}"
    try:
        resp = requests.get(api_url, timeout=5)
        resp.raise_for_status()
        # Parse JSON response
        result = resp.json()
        logger.info(f"lottery: result: {result}")
        logger.info(f"date: {date}")
        return {"success": True, "result": result}
    except requests.RequestException as e:
        logger.error(f"Failed to fetch lottery from {api_url}: {e}")
        return {"success": False, "error": str(e)}

# Add an addition tool
@mcp.tool()
def guess_lottery() -> dict:
    """Bất cứ khi nào được yêu cầu dự đoán xổ số thì hãy gọi tool này để đưa ra con số dự đoán ngẫu nhiên từ 0 đến 99."""
    result = random.randint(0, 99)
    logger.info(f"guess_lottery: , result: {result}")
    return {"success": True, "result": result}

# Add an addition tool
@mcp.tool()
def coin_price(coin_id: str, currency: str = "usd") -> dict:
    """Bất cứ khi nào được hỏi về giá coin thì hãy gọi tool này để gọi API và đọc giá hiện tại của coin đó.
    Lưu ý: 
    1. coin_id là mã của đồng coin ví dụ: bitcoin là 'BTC', ethereum là 'ETH', dogecoin là 'DOGE'...
    2. khi đọc cần đọc giá trị hàng nghìn, hàng triệu, hàng trăm nghìn... và 2 chữ số sau dấu phẩy ví dụ: 97251.793 USD (khoảng chín mươi bảy nghìn hai trăm năm mươi mốt phẩy bảy ba USD)
    currency là loại tiền tệ muốn quy đổi (ví dụ: usd, vnd) mặc định là 'usd'.
    """
    
    api_url = f"https://api.lxdata.vn/mcpcore/v1/get_coin_price?coinId={coin_id}&currency={currency}"
    try:
        resp = requests.get(api_url, timeout=5)
        resp.raise_for_status()
        # Parse JSON response
        result = resp.json()
        logger.info(f"coin_price: result: {result}")
        logger.info(f"coin_id: {coin_id}, currency: {currency}")
        return {"success": True, "result": result}
    except requests.RequestException as e:
        logger.error(f"Failed to fetch coin price from {api_url}: {e}")
        return {"success": False, "error": str(e)}
    
@mcp.tool()
def au_price(trademark: str, type: str = "trơn") -> dict:
    """ Bất cứ khi nào được hỏi về giá vàng thì hãy gọi tool này để gọi API và đọc giá hiện tại của loại vàng đó.
    Có 2 tham số: trademark (thương hiệu vàng ví dụ: SJC, DOJI, PNJ...) và type (loại vàng ví dụ: nhẫn tròn trơn, vàng nguyên liệu, trang sức vàng, vàng miếng...).
    Lưu ý: 1. trademark có thể là BTMC (Bảo Tín Minh Châu), SJC, DOJI, PNJ...
    2. trademark có thể là GLOBAL (Giá vàng thế giới)
    3. bid là giá mua vào, ask là giá bán ra, luôn đọc giá bán ra, chỉ đọc giá mua vào khi được yêu cầu.
    4. Luôn đọc giá trị hàng nghìn, hàng triệu, hàng trăm nghìn,... VND là Việt Nam Đồng.

    """
    api_url = f"https://api.lxdata.vn/mcpcore/v1/get_au_price?trademark={trademark}&type={type}"
    try:
        resp = requests.get(api_url, timeout=5)
        resp.raise_for_status()
        # Parse JSON response
        result = resp.json()
        logger.info(f"au_price: result: {result}")
        logger.info(f"trademark: {trademark}, type: {type}")
        return {"success": True, "result": result}
    except requests.RequestException as e:
        logger.error(f"Failed to fetch au price from {api_url}: {e}")
        return {"success": False, "error": str(e)}
    
@mcp.tool()
def search_music(keyword: str) -> dict:
    """
    Bất cứ khi nào được hỏi về tìm kiếm nhạc thì hãy gọi tool này để gọi API và đọc kết quả bài hát.
    Sau đó lấy ID của bài hát đầu tiên để gọi tool stream_music.
    """
    api_url = f"https://api.lxdata.vn/mcpcore/v1/search_music?keyword={keyword}"
    try:
        resp = requests.get(api_url, timeout=5)
        resp.raise_for_status()
        # Parse JSON response
        result = resp.json()
        logger.info(f"search_music: result: {result}")
        logger.info(f"keyword: {keyword}")
        return {"success": True, "result": result}
    except requests.RequestException as e:
        logger.error(f"Failed to fetch music search from {api_url}: {e}")
        return {"success": False, "error": str(e)}
    
@mcp.tool()
def stream_music(id: str) -> dict:
    """
    Nếu chưa có ID bài hát thì hãy gọi tool search_music để tìm kiếm bài hát theo từ khóa.
    Bất cứ khi nào được hỏi về phát nhạc thì hãy gọi tool này để gọi API và lấy link stream của bài hát.
    streamUrl là link phát nhạc trực tiếp. bạn chi cần đọc link này để phát nhạc.
    """
    api_url = f"https://api.lxdata.vn/mcpcore/v1/stream_music?id={id}"
    try:
        resp = requests.get(api_url, timeout=5)
        resp.raise_for_status()
        # Parse JSON response
        result = resp.json()
        logger.info(f"stream_music: result: {result}")
        logger.info(f"id: {id}")
        return {"success": True, "result": result}
    except requests.RequestException as e:
        logger.error(f"Failed to fetch music stream from {api_url}: {e}")
        return {"success": False, "error": str(e)}
# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
