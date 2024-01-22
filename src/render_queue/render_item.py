from pathlib import Path
from secrets import token_hex
from typing import Union, Tuple
from zipfile import ZipFile
from dotenv import load_dotenv, find_dotenv
import os

import src.face_timelapse as ft

load_dotenv(find_dotenv())
config = {
    'VID_DIR': os.getenv('VID_DIR', 'data/renders'),
    'TMP_DIR': os.getenv('TMP_DIR', 'data/tmp'),
    'UPLOAD_DIR': os.getenv('UPLOAD_DIR', 'data/archieves')
}

class RenderItem:
    def __init__(self) -> None:
        self.root_dir = None
        self.token = token_hex(16)
        self.filename = Path(config['UPLOAD_DIR']).joinpath(f"{self.token}.zip")
        self.status = 'Initialized'

    def render(self) -> None:
        if not self.filename.is_file():
            raise ValueError("Recieved a non existant file")
        self.status = 'Rendering'
        _, img_dir, frame_dir = self.__prepare_dirs(self.token)
        # Unzipping a file
        with ZipFile(self.filename, 'r') as f:
            f.extractall(img_dir)
        if not RenderItem.__img_dir_valid(img_dir):
            self.status = 'Failed'
            raise ValueError("Archive contained sub folders")
        video_path = ft.render_timelapse(
            img_dir, 
            Path(config['VID_DIR']).joinpath(f'{self.token}.mp4'),
            frame_dir
        )
        self.status = 'Done'
        self.wipe_dirs()
        return video_path

    def __prepare_dirs(
        self,
        root_dir: Union[str, os.PathLike]
    ) -> Tuple[Path, Path, Path]:
        """Creates all needed directories for rendering process. 
        - `root_dir` - current item's root dir
        - `img_dir` - dir for extracted photos
        - `frame_dir` - dir for aligned frames

        `img_dir` and `frame_dir` are child directores of `root_dir`

        Args:
            root_dir (Union[str, os.PathLike]): name of the item's root dir.
            This directory will be created in directory that is set in `TMP_DIR`
            env variable.

        Returns:
            Tuple[Path, Path, Path]: `root_dir`, `img_dir`, `frame_dir`
        """
        root_dir = Path(config['TMP_DIR']).joinpath(root_dir)
        os.mkdir(root_dir)
        self.root_dir = root_dir
        img_dir = root_dir.joinpath('img')
        os.mkdir(img_dir)
        frame_dir = root_dir.joinpath('frames')
        os.mkdir(frame_dir)
        return root_dir, img_dir, frame_dir
    
    @staticmethod
    def __img_dir_valid(img_dir: Union[str, os.PathLike]) -> bool:
        if not isinstance(img_dir, Path):
            img_dir = Path(img_dir)
        for item in img_dir.iterdir():
            if not Path(item).is_file():
                return False
        return True

    def wipe_dirs(self) -> None:
        if self.root_dir is None: return
        def rmdir(directory):
            directory = Path(directory)
            for item in directory.iterdir():
                if item.is_dir():
                    rmdir(item)
                else:
                    item.unlink()
            directory.rmdir()
        if self.root_dir.exists():
            rmdir(self.root_dir)
        if self.filename.exists():
            os.remove(self.filename)

    def __del__(self) -> None:
        self.wipe_dirs()
