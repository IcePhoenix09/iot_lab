import csv
from datetime import datetime
from models import Accelerometer, Gps, AggregatedData, Parking


class FileDatasource:
    def __init__(self, id: int, accel_filename: str, gps_filename: str, parking_filename: str) -> None:
        self.accel_filename = accel_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename
        self.user_id = id

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        self.f1 = open(self.accel_filename, 'r')
        self.f2 = open(self.gps_filename, 'r')
        self.f3 = open(self.parking_filename, 'r')
        self.accel_reader = csv.DictReader(self.f1)
        self.gps_reader = csv.DictReader(self.f2)
        self.parking_reader = csv.DictReader(self.f3)

    def read(self) -> tuple[AggregatedData, Parking]:
        """Повертає дані отримані з датчиків"""
        try:
            row_a = next(self.accel_reader)
            row_g = next(self.gps_reader)
            row_p = next(self.parking_reader)
        except (StopIteration, AttributeError):
            self.startReading()
            row_a = next(self.accel_reader)
            row_g = next(self.gps_reader)
            row_p = next(self.parking_reader)

        aggregated = AggregatedData(
            self.user_id,
            Accelerometer(int(row_a['x']), int(row_a['y']), int(row_a['z'])),
            Gps(float(row_g['longitude']), float(row_g['latitude'])),
            datetime.now()
        )
        
        parking = Parking(
            int(row_p['empty_count']),
            Gps(float(row_p['longitude']), float(row_p['latitude']))
        )
        
        return aggregated, parking

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        self.f1.close()
        self.f2.close()
        self.f3.close()
