# server.py
from mcp.server.fastmcp import FastMCP
import sys
import logging
import requests
import math
import random
import os
import json

logger = logging.getLogger('Calculator')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

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
    api_url = f"{base_url}/mcpcore/v1/get_weather?location={location}&date={date}"

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
    api_url = f"{base_url}/mcpcore/v1/get_lottery?region={region}&date={date}"
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
    
    api_url = f"{base_url}/mcpcore/v1/get_coin_price?coinId={coin_id}&currency={currency}"
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
    api_url = f"{base_url}/mcpcore/v1/get_au_price?trademark={trademark}&type={type}"
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
    api_url = f"{base_url}/mcpcore/v1/search_music?keyword={keyword}"
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
    streamUrl là link phát nhạc trực tiếp. bạn chi cần đọc link này sau đó gọi tool self.music.play_song và truyền tham số url vào song_id.
    """

    api_url = f"{base_url}/mcpcore/v1/stream_music?id={id}"
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
    
@mcp.tool()
def get_devices() -> dict:
    """Bất cứ khi nào được hỏi về danh sách thiết bị thông minh thì hãy gọi tool này
      để gọi API và lấy danh sách tất cả các thiết bị hiện có."""
    api_url = f"{base_url}/iotcore/v1.0/get_devices"
    try:
        logger.info(f'Calling get_devices with user: {basic_auth_user}')

        resp = requests.get(
            api_url,
            auth=(basic_auth_user, basic_auth_pass),
            timeout=5
        )
        resp.raise_for_status()

        result = resp.json()
        logger.info(f"get_devices: result: {result}")
        return {"success": True, "result": result}

    except requests.RequestException as e:
        logger.error(f"Failed to fetch all devices from {api_url}: {e}")
        return {"success": False, "error": str(e)}
    
@mcp.tool()
def control_device(device_id: str, device_type: str, command: str, options:dict=[]) -> dict:
    """Bất cứ khi nào được yêu cầu điều khiển thiết bị thông minh thì hãy gọi tool này
      để gọi API và điều khiển thiết bị theo device_id và command truyền vào.
      device_id: là ID của thiết bị cần điều khiển (lấy từ tool get_devices)
      device_type: là loại thiết bị cần điều khiển (lấy từ tool get_devices)
      options: là tùy chọn bổ sung cho lệnh điều khiển (nếu có) bao gồm:
        temperature: nhiệt độ (dùng cho điều hòa) trong khoảng từ 16 đến 30 độ C
        wind_speed: tốc độ gió (dùng cho điều hòa) trong khoảng từ 0 đến 3 (trong đó 0 là tự động) 
        mode: chế độ (dùng cho điều hòa) gồm: 0: Cool, 1: Hot, 2: Auto, 3: Fan, 4: Dehumy
      command: là lệnh điều khiển thiết bị được đọc từ file device_config.json tùy vào type lệnh điều khiển. bao gồm:
        POWER_ON: lệnh bật thiết bị
        POWER_OFF: lệnh tắt thiết bị
        SWING_ON: lệnh bật chế độ đảo gió (dùng cho điều hòa)
        SWING_OFF: lệnh tắt chế độ đảo gió (dùng cho điều
        CHANGE_SPEED: lệnh thay đổi tốc độ quạt (dùng cho quạt)
        SET_TEMPERATURE: lệnh đặt nhiệt độ (dùng cho điều hòa)
        SET_WIND_SPEED: lệnh đặt tốc độ quạt (dùng cho điều hòa)
        SET_MODE: lệnh đặt chế độ (dùng cho điều hòa)
      Lưu ý: không thay đổi chữ hoa, chữ thường trong code và giá trị."""
    
    logger.info(f'Received control_device with user: {basic_auth_user}, device_id: {device_id}, command: {command}', extra={"options": options})
    # Đọc file device_config.json để lấy lệnh điều khiển tương ứng
    # Tìm lệnh trong file device_config.json dựa trên device_type và command type
    with open('device_config.json', 'r', encoding='utf-8') as f:
        device_configs = json.load(f)
    for device in device_configs:
        if device['device_type'] == device_type:
            # Nếu device_type = "infrared_ac" và command = "SET_TEMPERATURE", cần thêm giá trị nhiệt độ từ options vào lệnh
            if device_type == "infrared_ac" and command == "SET_TEMPERATURE" and "temperature" in options:
                for cmd in device['commands']:
                    if command in cmd['type']:
                        # Cập nhật giá trị nhiệt độ trong lệnh
                        for data in cmd['data']:
                            if data['code'] == "T":
                                data['value'] = options['temperature']
                        command_json = json.dumps(cmd['data'])
                        break
            elif device_type == "infrared_ac" and command == "SET_WIND_SPEED" and "wind_speed" in options:
                for cmd in device['commands']:
                    if command in cmd['type']:
                        # Cập nhật giá trị tốc độ gió trong lệnh
                        for data in cmd['data']:
                            if data['code'] == "F":
                                data['value'] = options['wind_speed']
                        command_json = json.dumps(cmd['data'])
                        break
            elif device_type == "infrared_ac" and command == "SET_MODE" and "mode" in options:
                for cmd in device['commands']:
                    if command in cmd['type']:
                        # Cập nhật giá trị chế độ trong lệnh
                        for data in cmd['data']:
                            if data['code'] == "M":
                                data['value'] = options['mode']
                        command_json = json.dumps(cmd['data'])
                        break
            else:
                for cmd in device['commands']:
                    if command in cmd['type'] :
                        command_json = json.dumps(cmd['data'])
                        break

    api_url = f"{base_url}/iotcore/v1.0/control_device/{device_id}/command"
    payload = json.loads(command_json)
    # payload = {
    #     "device_id": device_id,
    #     "command": command
    # }
    try:
        logger.info(f'Calling control_device with user: {basic_auth_user}, device_id: {device_id}, command: {command}')

        resp = requests.post(
            api_url,
            json=payload,
            auth=(basic_auth_user, basic_auth_pass),
            timeout=5
        )
        resp.raise_for_status()

        result = resp.json()
        logger.info(f"control_device: result: {result}")
        return {"success": True, "result": result}

    except requests.RequestException as e:
        logger.error(f"Failed to control device from {api_url}: {e}")
        return {"success": False, "error": str(e)}

# Start the server
if __name__ == "__main__":
    base_url = os.environ.get("API_BASE_URL", "")
    basic_auth_user = os.environ.get("BasicAuthOptions__Username", "")
    basic_auth_pass = os.environ.get("BasicAuthOptions__Password", "")
    mcp.run(transport="stdio")
