from os import listdir, path, stat, mkdir
from typing import List, Tuple
from shutil import copyfile
from sys import exit
from PIL import Image
import imghdr

DEFAULT_WIN_BG_IMG_TYPES = ['tiff', 'jpeg']


def check_if_bg_img(file_path_: str, testers: List[str] = None) -> bool:
    if not testers:
        testers = _img_type_to_tester(DEFAULT_WIN_BG_IMG_TYPES)

    with open(file_path_, 'rb') as bg_img:
        metadata = bg_img.read(32)
        if any(map(lambda tester: tester(metadata, None), testers)):
            return True
    return False


def _get_img_type_tester(img_type: str) -> callable:
    tester_prefix = 'test_'
    try:
        return getattr(imghdr, tester_prefix + img_type)
    except KeyError:
        raise ('Couldn\'t find tester for image type: {}'.format(img_type))


def _img_type_to_tester(img_type_list: List[str]):
    return map(_get_img_type_tester, img_type_list)


def get_bg_images() -> List[str]:
    background_images = []
    win_img_path_loc = path.expandvars(get_win_img_bg_path())

    for file in listdir(win_img_path_loc):
        file_path = path.join(win_img_path_loc, file)
        if check_if_bg_img(file_path) and filter_by_img_weight(file_path):
            background_images.append(file_path)
    return background_images


def get_win_img_bg_path() -> str:
    return \
        r'%userprofile%\AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets'


def filter_by_img_weight(file_path_: str) -> bool:
    return True if stat(file_path_).st_size / 1000 > 400 else False


def _get_img_dimensions(img_path: str) -> Tuple[int, int]:
    # returns (width, length) tuple
    return Image.open(img_path).size


def _is_horizontal_img(img_path: str) -> bool:
    # True if horizontal, False if vertical
    width, length = _get_img_dimensions(img_path)
    return width >= length


if __name__ == '__main__':
    bg_image_list = get_bg_images()
    if not bg_image_list:
        exit()

    save_dir = path.expanduser(r'~\Desktop')
    horizontal_img_dir = path.join(save_dir, 'Horizontal-Background-Images')
    vertical_img_dir = path.join(save_dir, 'Vertical-Background-Images')

    if not path.isdir(horizontal_img_dir):
        mkdir(horizontal_img_dir)
    if not path.isdir(vertical_img_dir):
        mkdir(vertical_img_dir)

    for image in bg_image_list:
        file_name = path.join(path.basename(image) + '.' + imghdr.what(image))
        save_path = path.join(horizontal_img_dir, file_name) if _is_horizontal_img(image) else \
            path.join(vertical_img_dir, file_name)
        if not path.isfile(save_path):
            copyfile(image, save_path)
