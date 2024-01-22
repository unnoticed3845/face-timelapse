import cv2
from pathlib import Path
from os import listdir, mkdir, system
from tqdm import tqdm

from . import align, detect_mul

def render_timelapse(
    photo_dir: str,
    out_vid_name: str,
    frame_dir: str,
    fps: int = 10,
    del_out_frames: bool = True
) -> str:
    # validating input dir
    photo_dir = Path(photo_dir)
    if not photo_dir.is_dir():
        raise ValueError(f"Input dir {photo_dir} does not exist or invalid")
    # getting photo paths
    photo_paths = [
        str(photo_dir.joinpath(x))
        for x in sorted(listdir(photo_dir))
    ]
    #photo_paths *= 10

    # Pipeline
    # detecting faces
    wrapped_paths = tqdm(photo_paths, desc='Detecting faces')
    detected = list(detect_mul(wrapped_paths))

    # aligning faces (tqdm inside align() func)
    aligned = align(detected)

    # validating output dir
    out_dir = Path(frame_dir)
    if not (out_dir.exists() and out_dir.is_dir()):
        mkdir(out_dir)
    # saving images for ffmpeg
    wrapped_aligned = tqdm(range(len(aligned)), desc='Saving images')
    for i in wrapped_aligned:
        #img_rgb = cv2.cvtColor(aligned[i], cv2.COLOR_BGR2RGB)
        f_name = f"{i}".zfill(6) + ".jpg"
        cv2.imwrite(str(out_dir.joinpath(f_name)), aligned[i])

    # rendering with ffmpeg
    ffmpeg = f"ffmpeg -y -framerate {fps} -i {out_dir}/%06d.jpg -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p {out_vid_name}"
    system(ffmpeg)
    print(f"Output video was saved as {out_vid_name}")
    
    # Removing out photos
    if del_out_frames:
        def rmdir(directory):
            directory = Path(directory)
            for item in directory.iterdir():
                if item.is_dir():
                    rmdir(item)
                else:
                    item.unlink()
            directory.rmdir()
        rmdir(out_dir)
        print(f"Out photos directory was removed")
    
    return out_vid_name
