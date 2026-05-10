import csv
import random
from datetime import datetime
from models import Accelerometer, Gps, AggregatedData, Parking

class FileDatasource:
    def __init__(self, id: int, accel_filename: str, gps_filename: str, parking_filename: str) -> None:
        self.accel_filename = accel_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename
        self.user_id = id
        
        # Load all parking spaces into memory with an auto-generated ID
        self.parking_data = []
        with open(self.parking_filename, 'r') as f:
            reader = csv.DictReader(f)
            # Enumerate generates IDs starting from 1
            for i, row in enumerate(reader, start=1):
                self.parking_data.append({
                    'parking_id': i,
                    'empty_count': int(row['empty_count']),
                    'longitude': float(row['longitude']),
                    'latitude': float(row['latitude'])
                })

    def get_initial_parking_states(self) -> list[Parking]:
        """Returns the current state of ALL parking sensors."""
        states = []
        for spot in self.parking_data:
            states.append(Parking(
                parking_id=spot['parking_id'],
                empty_count=spot['empty_count'],
                gps=Gps(longitude=spot['longitude'], latitude=spot['latitude']),
                time=datetime.now()
            ))
        return states

    def startReading(self, *args, **kwargs):
        self.f1 = open(self.accel_filename, 'r')
        self.f2 = open(self.gps_filename, 'r')
        self.accel_reader = csv.DictReader(self.f1)
        self.gps_reader = csv.DictReader(self.f2)

    def read(self) -> tuple[AggregatedData, Parking]:
        """Повертає дані отримані з датчиків"""
        try:
            row_a = next(self.accel_reader)
            row_g = next(self.gps_reader)
        except (StopIteration, AttributeError):
            self.startReading()
            row_a = next(self.accel_reader)
            row_g = next(self.gps_reader)

        aggregated = AggregatedData(
            self.user_id,
            Accelerometer(int(row_a['x']), int(row_a['y']), int(row_a['z'])),
            Gps(float(row_g['longitude']), float(row_g['latitude'])),
            datetime.now()
        )
        
        # Randomly pick ONE spot to update for the continuous stream
        spot = random.choice(self.parking_data)
        change = random.choice([-1, 0, 1])
        spot['empty_count'] = max(0, spot['empty_count'] + change)
        
        parking = Parking(
            parking_id=spot['parking_id'],
            empty_count=spot['empty_count'],
            gps=Gps(longitude=spot['longitude'], latitude=spot['latitude']),
            time=datetime.now()
        )
        
        return aggregated, parking

    def stopReading(self, *args, **kwargs):
        self.f1.close()
        self.f2.close()