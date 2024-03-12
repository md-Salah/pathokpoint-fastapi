import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="xyz",
    api_key="xyz",
    api_secret="xyz"
)


x = cloudinary.uploader.upload("dummy/a.JPG",
public_id = "olympic_flag")

print(x)

# url, options = cloudinary.utils.cloudinary_url("olympic_flag", width=100, height=150, crop="fill")

# print(url)
# print(options)

# res = cloudinary.CloudinaryImage("olympic_flag").image(effect='background_removal')

# print(res)

