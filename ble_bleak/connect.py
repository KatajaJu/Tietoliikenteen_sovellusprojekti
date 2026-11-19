import asyncio
from bleak import BleakClient

address = "DA:68:47:B5:26:F0"
MODEL_NBR_UUID = "00002a05-0000-1000-8000-00805f9b34fb"

async def main(address):
    async with BleakClient(address) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print(f"Model Number: {model_number.decode()}")

asyncio.run(main(address))