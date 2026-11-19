import asyncio
import requests
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "MY_LBS2_VIM"
CHARACTERISTIC_UUID = "00001526-1212-efde-1523-785feabcd123"
SERVER_URL = "http://172.20.241.117:5000/data"
GROUP_ID = 9

async def send_to_server(session, data, mac):

    payload = {
        "data": data.hex(),
        "groupid": GROUP_ID,
        "from_mac": mac,
        "to_mac": "0"
    }

    for attempt in range(5):

        try:
            response = await asyncio.to_thread(
                session.post,
                SERVER_URL,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                print("Tallennettu:", data.hex())
                return True

            print("Server error:", response.status_code)

        except requests.RequestException as e:
            print("Yhteysvirhe:", e)

        await asyncio.sleep(1 + attempt)

    print("Lähetys epäonnistui:", data.hex())
    return False

async def main():

    session = requests.Session()

    while True:

        try:
            print("Etsitään nRF5340-laitetta...")

            device = await BleakScanner.find_device_by_name(
                DEVICE_NAME,
                timeout=15
            )

            if device is None:
                print("Laitetta ei löydy.")
                await asyncio.sleep(3)
                continue

            print("Laite löytyi:", device.address)

            queue = asyncio.Queue()

            async with BleakClient(device) as client:

                print("Bluetooth yhdistetty!")

                def notification_handler(sender, data):

                    print("Bluetooth data:", data.hex())

                    try:
                        queue.put_nowait(
                            (bytes(data), device.address)
                        )
                    except asyncio.QueueFull:
                        print("VAROITUS: lähetysjono täynnä")

                await client.start_notify(
                    CHARACTERISTIC_UUID,
                    notification_handler
                )

                async def sender_worker():

                    while True:
                        data, mac = await queue.get()

                        try:
                            await send_to_server(
                                session,
                                data,
                                mac
                            )
                        finally:
                            queue.task_done()

                worker = asyncio.create_task(sender_worker())

                print("Odotetaan Bluetooth-dataa...")

                try:
                    while client.is_connected:
                        await asyncio.sleep(1)
                finally:
                    worker.cancel()
                    await asyncio.gather(
                        worker,
                        return_exceptions=True
                    )

        except Exception as e:
            print("Bluetooth virhe:", e)

        print("Yhteys katkesi. Yritetään uudelleen...")
        await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
