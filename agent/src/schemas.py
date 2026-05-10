from marshmallow import Schema, fields

class AccelerometerSchema(Schema):
    x = fields.Int()
    y = fields.Int()
    z = fields.Int()

class GpsSchema(Schema):
    longitude = fields.Float()
    latitude = fields.Float()

class AggregatedDataSchema(Schema):
    user_id = fields.Int()
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    time = fields.DateTime('iso')

class ParkingSchema(Schema):
    parking_id = fields.Int()
    empty_count = fields.Int()
    gps = fields.Nested(GpsSchema)
    time = fields.DateTime('iso')