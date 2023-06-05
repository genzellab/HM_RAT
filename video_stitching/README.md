
# Video stitching :video_camera:

The following scripts stitch the 12 hexmaze eyes into a single video.

- stitch.py  (For Windows)
- join_views.py  (For linux)  Depending on the computer GPU you are using you may need to change [this line](https://github.com/genzellab/HM_RAT/blob/main/video_stitching/join_views.py#L96) for:     `cmd += '-c:v libx264 -b:v 4000k -preset ultrafast -pix_fmt yuv420p'`

Instructions for installing in Windows:

- Hexmaze stitcher installation.docx
