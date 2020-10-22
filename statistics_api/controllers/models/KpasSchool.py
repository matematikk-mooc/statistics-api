class KpasSchool:
    """Value class containing org number, name and geographical coordinates"""
    def __init__(self, organization_number: int, name: str, latitude: str, longitude: str):
        self.organization_number = organization_number
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
