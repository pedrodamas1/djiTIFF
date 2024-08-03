import os
from PIL import Image, ImageOps
from exif import Image as ExifImage
# from osgeo import gdal, osr
import math



def get_exif_data(image_path):
    with open(image_path, 'rb') as image_file:
        img = ExifImage(image_file)
        
    if img.has_exif:
        latitude = img.gps_latitude
        latitude_ref = img.gps_latitude_ref
        longitude = img.gps_longitude
        longitude_ref = img.gps_longitude_ref
        altitude = img.gps_altitude
        rel_altitude = img.relative_altitude
        yaw = img.get('yaw', 0)  # Default to 0 if not available
        focal_length = img.get('focal_length', 8.8)  # Example default value (in mm)

        # Convert to decimal degrees
        lat = (latitude[0] + latitude[1] / 60 + latitude[2] / 3600) * (-1 if latitude_ref == 'S' else 1)
        lon = (longitude[0] + longitude[1] / 60 + longitude[2] / 3600) * (-1 if longitude_ref == 'W' else 1)
        return lat, lon, altitude, rel_altitude, focal_length, yaw
    else:
        raise ValueError("Image does not contain EXIF data")

def calculate_pixel_size(focal_length, altitude, image_width, sensor_width=13.2):
    # Calculate GSD in meters per pixel
    gsd_m_per_pix = (sensor_width * altitude) / (focal_length * image_width)
    # Convert GSD to degrees per pixel
    gsd_deg_per_pix = gsd_m_per_pix / 111320
    return gsd_deg_per_pix

def rotate_image(image_path, yaw):
    image = Image.open(image_path)
    # Convert yaw to degrees counterclockwise
    yaw_deg = -yaw
    rotated_image = ImageOps.exif_transpose(image.rotate(yaw_deg, expand=True))
    return rotated_image

def create_geotiff(image, output_path, lat, lon, pixel_size):
    width, height = image.size

    # Create a new GDAL dataset
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(output_path, width, height, 3, gdal.GDT_Byte)

    # Set the projection and geotransform
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # WGS84
    dataset.SetProjection(srs.ExportToWkt())

    # Calculate the geotransform
    geotransform = [lon, pixel_size, 0, lat, 0, -pixel_size]
    dataset.SetGeoTransform(geotransform)

    # Write the image data to the geotiff
    for i in range(3):  # Assuming RGB image
        band = dataset.GetRasterBand(i + 1)
        band.WriteArray(image.split()[i])

    dataset.FlushCache()

if __name__ == "__main__":
    input_image_path = 'bne.jpg'
    output_geotiff_path = 'path/to/your/output.tif'

    img = Image.open('bne.jpg')
    exif_data = img._getexif()
    print(exif_data)
    
    # lat, lon, altitude, rel_altitude, focal_length, yaw = get_exif_data(input_image_path)
    
    # image = Image.open(input_image_path)
    # image_width, image_height = image.size
    
    # # Calculate pixel size (degrees per pixel)
    # pixel_size = calculate_pixel_size(focal_length, rel_altitude, image_width)
    
    # # Rotate the image to align with north
    # rotated_image = rotate_image(input_image_path, yaw)
    
    # # Create the georeferenced image
    # create_geotiff(rotated_image, output_geotiff_path, lat, lon, pixel_size)
    
    # print(f"Georeferenced image saved to {output_geotiff_path}")
