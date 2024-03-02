import datetime
import json
import time
import asyncio

import bleak
from sensorpush import sensorpush as sp

if __name__ == "__main__":
    async def read_temp():
        devices = await bleak.BleakScanner.discover(timeout=10)
        for d in devices:
            if d.name is not None:
                if 'SensorPush' in d.name:
                    client = bleak.BleakClient(d.address)
                    await client.connect()
                    temp = await sp.read_temperature(client)
                    await client.disconnect()
                    data = {
                        'temp': temp,
                        'timestamp': datetime.datetime.utcnow().isoformat()
                    }
                    with open('temperature_reading.json', 'w') as f:
                        f.write(json.dumps(data))
                    time.sleep(30)

    async def read_temp_loop():
        while True:
            try:
                await read_temp()
            except bleak.exc.BleakDeviceNotFoundError:
                continue
            except asyncio.exceptions.TimeoutError:
                time.sleep(5)
                continue

    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_temp_loop())
