# Media Storage Setup for Render (Cloudinary)

This project already supports Cloudinary-based media storage in Django settings.
When the 3 Cloudinary environment variables are set, uploads are stored in Cloudinary instead of Render local disk.

## Why this is needed

Render web service local disk can be ephemeral, so uploaded files may disappear after redeploy/restart.
Cloud storage keeps uploaded images persistent.

## 1) Configure environment variables in Render

In your Render Web Service, set:

- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET

These are also declared in render.yaml for blueprint-based deploys.

## 2) Verify Django behavior

Settings logic in this project:

- Enables Cloudinary only when all 3 variables are present.
- Switches DEFAULT_FILE_STORAGE to Cloudinary storage.

Once enabled, new uploaded images (hero/gallery/cakes) are stored remotely.

## 3) Redeploy and test

1. Trigger a deploy on Render after setting env vars.
2. Upload a new hero image from manager flow.
3. Refresh homepage and confirm image URL points to Cloudinary domain.

## 4) Existing local media files

Images uploaded before Cloudinary setup may still reference old local paths.
Re-upload important images after Cloudinary is enabled.

## Notes

- Static files (CSS/JS) are separate from media uploads and continue to use collectstatic/WhiteNoise.
- If you do not want Cloudinary, use a Render persistent disk and map MEDIA_ROOT there.
