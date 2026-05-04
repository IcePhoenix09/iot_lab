import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from kivy.logger import Logger
from lineMapLayer import LineMapLayer
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self.car_marker = None
        self.map_layer = None
        self.datasource = Datasource(user_id=1)

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        self.map_layer = LineMapLayer()
        self.mapview.add_layer(self.map_layer, mode="scatter")
        
        # Ініціалізація маркера для авто (відразу ставимо в центр Києва, щоб її було видно до початку руху)
        self.car_marker = MapMarker(lat=50.4501, lon=30.5234, source="images/car.png")
        self.mapview.add_widget(self.car_marker)

        # Оновлення даних мапи, наприклад, щосекунди
        Clock.schedule_interval(self.update, 1.0)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        points = self.datasource.get_new_points()
        if points:
            Logger.info(f"Map: Отримано {len(points)} нових точок для малювання!")
        
        for point in points:
            # Припускаємо, що point - це кортеж або список: (latitude, longitude, стан_дороги)
            lat, lon = point[0], point[1]
            state = point[2] if len(point) > 2 else "normal"
            
            self.update_car_marker((lat, lon))
            self.map_layer.add_point((lat, lon))
            
            if state == "pothole":
                self.set_pothole_marker((lat, lon))
            elif state == "bump":
                self.set_bump_marker((lat, lon))

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        self.mapview.remove_widget(self.car_marker)
        self.car_marker.lat = point[0]
        self.car_marker.lon = point[1]
        self.mapview.add_widget(self.car_marker)
        self.mapview.center_on(point[0], point[1])

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        pothole = MapMarker(lat=point[0], lon=point[1], source="images/pothole.png")
        self.mapview.add_widget(pothole)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        bump = MapMarker(lat=point[0], lon=point[1], source="images/bump.png")
        self.mapview.add_widget(bump)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView(zoom=15, lat=50.4501, lon=30.5234)
        return self.mapview


async def main():
    app = MapViewApp()
    await app.async_run(async_lib="asyncio")

if __name__ == '__main__':
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
